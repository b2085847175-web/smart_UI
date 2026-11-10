"""请求级兜底；未知POST不放行，GET仍不能被当成无副作用证明。"""
import re
from urllib.parse import parse_qsl, unquote, urlsplit


READ_POSTS = frozenset({"/api/work-order", "/api/ai-quality-inspection/list"})
READ_GETS = frozenset({"/api/yanzhi/recharge/records"})
DANGEROUS_PATH = re.compile(
    r"(?:^|[/_.-])(save|update|insert|create|delete|remove|enable|disable|toggle|"
    r"sync|subscribe|unsubscribe|upload|recharge|purchase|pay|logout|reset|"
    r"generate|export|import|check|mark|accept|reject|clear)(?:[/_.-]|$)", re.I
)
STATIC_TYPES = frozenset({"script", "stylesheet", "image", "font", "media"})
READINESS = """
(() => {
  window.__smokePending = 0;
  window.__smokeLastActivity = performance.now();
  const begin = () => { window.__smokePending++; window.__smokeLastActivity = performance.now(); };
  const end = () => { window.__smokePending = Math.max(0, window.__smokePending - 1); window.__smokeLastActivity = performance.now(); };
  const fetch = window.fetch;
  window.fetch = function(...args) { begin(); return fetch.apply(this, args).finally(end); };
  const send = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function(...args) { begin(); this.addEventListener('loadend',end,{once:true}); try { return send.apply(this,args); } catch(e) { end(); throw e; } };
})();
"""
BLOCK_CHANNELS = """
(() => {
  const deny = function() { throw new Error('Readonly smoke: realtime channel blocked'); };
  window.WebSocket = deny;
  window.EventSource = deny;
  // 当前Playwright对Worker实时连接拦截没有验证闭环，直接禁止创建Worker。
  window.Worker = deny;
  window.SharedWorker = deny;
  if (navigator.sendBeacon) navigator.sendBeacon = () => false;
})();
"""


def origin(url):
    parts = urlsplit(url)
    return parts.scheme.lower(), parts.netloc.lower()


class ReadOnlyPolicy:
    def __init__(self, base_url):
        self.base_url = base_url
        self.blocked = []
        self.auth = None
        self.auth_used = False

    def begin_login(self, username, password):
        self.auth = (username, password)
        self.auth_used = False

    def end_login(self):
        self.auth = None

    def permits(self, method, url, resource_type="fetch", payload=None, frame_url=""):
        path = urlsplit(url).path
        same_origin = origin(url) == origin(self.base_url)
        api = path.startswith("/api/")
        if not api and method in {"GET", "HEAD"} and resource_type in STATIC_TYPES:
            return True, "static resource"
        if not same_origin:
            return False, "cross-origin non-static request"
        normalized = re.sub(r"([a-z])([A-Z])", r"\1-\2", unquote(path))
        query = parse_qsl(urlsplit(url).query)
        action_keys = {"action", "operation", "command", "cmd", "method", "op"}
        if api and any(key.lower() in action_keys and DANGEROUS_PATH.search("/" + value) for key, value in query):
            return False, "write-like query action"
        if api and DANGEROUS_PATH.search(normalized) and path not in READ_GETS:
            return False, "write-like API path"
        # 仅登录页中携带本次账号和密码的单个认证POST可例外，不记录请求体。
        if self.auth and not self.auth_used and method == "POST":
            if (urlsplit(frame_url).path.rstrip("/") == "/login" and path == "/api/auth/login"
                    and isinstance(payload, dict)
                    and payload.get("account") == self.auth[0]
                    and payload.get("password") == self.auth[1]
                    and set(payload) == {"account", "password"}):
                self.auth_used = True
                return True, "one-shot authentication"
        if method == "POST" and path in READ_POSTS:
            # 接口语义已核实为查询；额外拒绝携带动作指令的异常请求体。
            def has_command(value):
                if isinstance(value, dict):
                    return any(str(key).lower() in action_keys or has_command(item) for key, item in value.items())
                if isinstance(value, list):
                    return any(has_command(item) for item in value)
                return False
            if has_command(payload):
                return False, "unexpected query command payload"
            return True, "verified readonly query"
        if method not in {"GET", "HEAD", "OPTIONS"}:
            return False, "unverified non-read method"
        if path.startswith("/api/") and DANGEROUS_PATH.search(path) and path not in READ_GETS:
            return False, "write-like API path"
        return True, "read method"

    def safe_path(self, url):
        path = urlsplit(url).path
        if self.auth:
            for secret in self.auth:
                path = path.replace(secret, "[redacted]")
        return path

    def install(self, context):
        context.route("**/*", self.route)
        # 在连接服务器前关闭，覆盖页面与Worker发起的新WebSocket。
        context.route_web_socket("**/*", self.block_websocket)
        context.add_init_script(BLOCK_CHANNELS + READINESS)

    def block_websocket(self, socket):
        self.blocked.append({"method": "WEBSOCKET", "path": self.safe_path(socket.url),
                             "reason": "realtime channel forbidden"})
        socket.close(code=1008, reason="readonly smoke")

    def route(self, route):
        request = route.request
        payload = None
        if request.method == "POST" and (self.auth or urlsplit(request.url).path in READ_POSTS):
            try:
                payload = request.post_data_json
            except Exception:
                payload = None
        try:
            frame_url = request.frame.url
        except Exception:
            frame_url = ""
        allowed, reason = self.permits(
            request.method, request.url, request.resource_type, payload, frame_url
        )
        if allowed:
            route.continue_()
        else:
            self.blocked.append({
                "method": request.method, "path": self.safe_path(request.url),
                "reason": reason,
            })
            route.abort("blockedbyclient")

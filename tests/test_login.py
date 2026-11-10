"""示例用例：SauceDemo 登录流程。验证框架可用后按此模式扩展。"""
import allure
import pytest

from pages.login_page import LoginPage

VALID_USER = "standard_user"
VALID_PASSWORD = "secret_sauce"


@allure.feature("登录")
class TestLogin:

    @pytest.mark.smoke
    @allure.story("正常登录")
    def test_login_success(self, page, base_url):
        login_page = LoginPage(page, base_url)
        login_page.open()
        login_page.login(VALID_USER, VALID_PASSWORD)
        login_page.should_have_url("inventory")

    @allure.story("错误密码提示")
    def test_login_with_wrong_password(self, page, base_url):
        login_page = LoginPage(page, base_url)
        login_page.open()
        login_page.login(VALID_USER, "wrong_password")
        assert "Username and password do not match" in login_page.get_error_message()

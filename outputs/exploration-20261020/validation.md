# Final validation (2026-10-20)

- Browser exploration: in-app browser, development site, Tmall B1 shop.
- Registered routes observed: 30/30.
- Business catalog: 84 scenarios; 23 verified operations, 20 inspected states, 41 not run.
- Offline verification: 19 passed, 7 online tests skipped, no warnings.
- Root collection: 265 tests collected successfully.
- Explicit B1 opt-in collection: 7 tests collected successfully.
- Explicit smoke opt-in collection: 237 tests collected successfully.
- No terminal browser automation was executed.
- Fixed root collection by registering smoke and B1 CLI options in root conftest.py; nested test directories retain their existing execution guards.
- Zhiyan credential fills no longer use the input-logging BasePage.fill helper.

Evidence: checkpoint.json, coverage-summary.json, offline-tests.xml, collection.txt,
smoke-collection.txt, and 12 PNG screenshots in this directory.

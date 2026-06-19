from playwright.sync_api import Page


class BasePage:

    def __init__(self, page):
        self.page = page

    def _log(self, accion, detalle, ok=True):
        icono = "OK" if ok else "ERROR"
        check = "  ✅" if ok else "  ❌"
        print(f"[{icono}]{check} {accion}: {detalle}")

    def navigate(self, url):
        self._log("NAV", url)
        self.page.goto(url)

    def click(self, locator, label):
        self._log("CLICK", label)
        locator.click()

    def fill(self, locator, value, label):
        masked = value if "password" not in label.lower() and "pass" not in label.lower() else "****"
        self._log("FILL", f"{label} = '{masked}'")
        locator.fill(value)

    def select(self, locator, value=None, label="", **kwargs):
        display = value if value else str(kwargs)
        self._log("SELECT", f"{label} → '{display}'")
        if value is not None:
            locator.select_option(value)
        else:
            locator.select_option(**kwargs)

    def wait_for_url(self, pattern):
        self.page.wait_for_url(pattern)

    def screenshot(self, name):
        import os
        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path=f"screenshots/{name}.png")
        self._log("SCREENSHOT", name)

    def verify(self, condition, label, extra=""):
        ok = condition
        self._log("CHECK", f"{label} {extra}", ok)
        return ok

    def info(self, msg):
        print(f"[INFO]  ℹ️  {msg}")

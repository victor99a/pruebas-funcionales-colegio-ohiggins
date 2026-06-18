from playwright.sync_api import Page


class BasePage:
    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        self.page.goto(url)

    def wait_for_url(self, pattern):
        self.page.wait_for_url(pattern)

    def screenshot(self, name):
        self.page.screenshot(path=f"screenshots/{name}.png")

    def get_text(self, locator):
        return self.page.locator(locator).text_content()

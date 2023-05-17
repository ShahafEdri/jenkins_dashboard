import re
import webbrowser

class BrowserController:
    def __init__(self, browser):
        self.browser = browser

    def open(self, url):
        # remove double slashes
        url = re.sub(r'(?<!:)/{2,}', '/', url)
        self.browser.open(url)

    def close(self):
        self.browser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class ChromeController(BrowserController):
    def __init__(self):
        chrome_path = "/usr/bin/google-chrome-stable"
        webbrowser.register('chrome',None,webbrowser.BackgroundBrowser(chrome_path))
        super().__init__(webbrowser.get('chrome'))


if __name__ == "__main__":
    with ChromeController() as chrome:
        chrome.open("https://pl-jenkins01:8443/job/request_runner/48707/")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from config import config
from cache_api import Cache


class TestManagerAPI:
    def __init__(self):
        self.base_url = config["test_manager_url"]
        self.base_url_node = self.base_url + "/nodes"
        self.cache_file = 'cache_test_manager.json'
        self.cache = Cache(self.cache_file, 3*60)

    def is_server_hold_on_failure(self, server):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1200")
        chrome_options.add_argument("--headless")  # run the browser in the background
        base = '/html/body/div[2]/div[1]/table/tbody/'
        element_div_xpath1 = 'tr/'
        element_div_xpath2 = 'tr[2]/'
        font = 'td[2]/font'
        job_number = 'td[14]/a'
        try:
            driver = webdriver.Chrome(options=chrome_options, executable_path=ChromeDriverManager().install())
            # driver = webdriver.Chrome(options=chrome_options, executable_path="/usr/bin/chromedriver")
            # Get the URL
            url = f"{self.base_url_node}/{server}"
            driver.get(url)

            # check if the element exists
            if not driver.find_elements(by=By.XPATH, value=base+element_div_xpath2+font):
                if not driver.find_elements(by=By.XPATH, value=base+element_div_xpath1+font):
                    return False
                base_xpath = base + element_div_xpath1
            else:
                base_xpath = base + element_div_xpath2

            # Extract the data from the element
            failed_div_element = driver.find_element(by=By.XPATH, value=base_xpath+font)
            if failed_div_element.text == "failed":
                job_name_and_build_number = failed_div_element.find_element(by=By.XPATH, value=base_xpath+job_number).text
                return job_name_and_build_number

        except Exception as e:
            print(f"An error occurred while checking URL: {e}")
            return "error"
        finally:
            if locals().get('driver'):
                driver.quit()

    def is_build_hold_on_failure_on_server(self, server, build_number):
        if self.cache.is_cache_expired(key=server):
            status = self._get_build_hold_on_failure_on_server(server, build_number)
            self.cache[server] = status
        else:
            status = self.cache[server]
        return status

    def _get_build_hold_on_failure_on_server(self, server, build_number):
        fetched_build_name_and_number = self.is_server_hold_on_failure(server)
        if fetched_build_name_and_number == "error":
            return "error"
        elif not fetched_build_name_and_number:
            return False
        else:
            build_name, fetched_build_number = fetched_build_name_and_number.split(" #")
            if int(fetched_build_number) == int(build_number):
                return True
            return False


if __name__ == '__main__':
    test_manager_api = TestManagerAPI()
    print(test_manager_api.is_server_hold_on_failure("Lab4023"))
    print(test_manager_api.is_server_hold_on_failure("Lab6002"))
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab6002", 23622))
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab4023", 26620))
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab4022", 23621))

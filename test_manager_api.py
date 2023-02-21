from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import config


class TestManagerAPI:
    def __init__(self):
        self.base_url = config["test_manager_url"]
        self.base_url_node = self.base_url + "/nodes"

    def is_server_hold_on_failure(self, server):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1200")
        chrome_options.add_argument("--headless")  # run the browser in the background
        driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

        # failure_element_div_xpath = '//*[@id="DataTables_Table_0"]/tbody/tr[2]'
        failure_element_div_xpath = '/html/body/div[2]/div[1]/table/tbody/tr[2]/td[2]/font'
        job_number_xpath = '/html/body/div[2]/div[1]/table/tbody/tr[2]/td[14]/a'

        try:
            # Get the URL
            url = f"{self.base_url_node}/{server}"
            driver.get(url)

            # check if the element exists
            if not driver.find_elements(by=By.XPATH, value=failure_element_div_xpath):
                return False

            # Extract the data from the element
            failed_div_element = driver.find_element(by=By.XPATH, value=failure_element_div_xpath)
            if failed_div_element.text == "failed":
                job_name_and_build_number = driver.find_element(by=By.XPATH, value=job_number_xpath).text
                return job_name_and_build_number

        except Exception as e:
            print(f"An error occurred while checking URL: {e}")
            return "error"
        finally:
            driver.quit()

    def is_build_hold_on_failure_on_server(self, server, build_number):
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
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab4023", 23622))
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab4023", 23621))
    print(test_manager_api.is_build_hold_on_failure_on_server("Lab4022", 23621))

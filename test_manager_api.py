from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config

class TestManagerAPI:
    def __init__(self):
        self.base_url = config["test_manager_url"]
        self.base_url_node = self.base_url + "/node"

    def is_server_hold_on_failure(self, server):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # run the browser in the background
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Get the URL
            url = f"{self.base_url_node}/{server}"
            driver.get(url)

            # Wait for the element to load
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="DataTables_Table_0"]/tbody/tr[2]/td[2]/text()[2]')))

            # Extract the data from the element
            data = element.get_attribute("textContent")
            return data.strip()

        except Exception as e:
            print(f"An error occurred while checking URL: {e}")
            return "error"
        finally:
            driver.quit()

if __name__ == '__main__':
    test_manager_api = TestManagerAPI()
    print(test_manager_api.is_server_hold_on_failure("Lab4023"))







if __name__ == '__main__':
    test_manager_api = TestManagerAPI()
    xpath = '//*[@id="DataTables_Table_0"]/tbody/tr[2]/td[2]/text()[2]'
    server = "Lab4023"
    element_text = test_manager_api.get_element_text(server, xpath)
    print(element_text)

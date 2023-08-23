from cache_api import Cache
from config import config
from web_utils import WebUtils

# change the class to work with the test manager api form example: http://pl-test-manager:5000/api/v1/nodes/lab4012 to get the failures
class TestManagerAPI:
    def __init__(self):
        self.base_url = config["test_manager_url"]
        self.cache_file = 'cache_test_manager.json'
        self.cache = Cache(self.cache_file, 3*60)
        self.web_utils = WebUtils()

    def is_server_hold_on_failure(self, server):
        response = self.web_utils._make_get_request(f"{self.base_url}/api/v1/nodes/{server}")
        if response:
            if response["requests"]:
                # find list index of "request_runner" job in ["requests"][{list_index}]["job_name"]
                request_runner_index = next((index for (index, d) in enumerate(response["requests"]) if d["job_name"] == "request_runner"), None)
                if request_runner_index is None:
                    return False
                hof_status = response["requests"][request_runner_index]["status_info"]
                if hof_status == "hold-on-failure":
                    return response["requests"][request_runner_index]["build_number"]
                else:
                    return False
            else:
                return False
        elif response is None:
            return None
        else:
            return "error"

    def is_build_hold_on_failure_on_server(self, server, build_number):
        status = self._get_build_hold_on_failure_on_server(server, build_number)
        return status

    from general_utils import timeit
    @timeit
    def _get_build_hold_on_failure_on_server(self, server, build_number):
        fetched_build_number = self.is_server_hold_on_failure(server)
        if fetched_build_number == "error":
            return "error"
        elif not fetched_build_number:
            return False
        else:
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
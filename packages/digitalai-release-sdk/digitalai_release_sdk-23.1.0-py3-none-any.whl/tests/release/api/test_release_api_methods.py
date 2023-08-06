import unittest

from digitalai.release.v1 import Configuration, ApiClient
from digitalai.release.v1.api.configuration_api import ConfigurationApi
from digitalai.release.v1.api.release_api import ReleaseApi
from digitalai.release.v1.model.release import Release
from digitalai.release.v1.model.variable import Variable


class TestReleaseApiMethods(unittest.TestCase):

    def test_api_methods(self):
        configuration = Configuration(host="http://localhost:5516", username='admin', password='admin')
        api_client = ApiClient(configuration)

        configuration_api = ConfigurationApi(api_client)
        variable_list: [Variable] = configuration_api.get_global_variables()
        print(f"variable_list : {variable_list}\n")

        release_api = ReleaseApi(api_client)
        release_list: [Release] = release_api.get_releases(depth=1, page=0, results_per_page=1)
        print(f"release_list : {release_list}\n")


if __name__ == '__main__':
    unittest.main()

import json
import os
import subprocess
import unittest


class TestWrapper(unittest.TestCase):

    def test_wrapper(self):
        """
        This test method sets the environment variables INPUT_LOCATION and OUTPUT_LOCATION,
        then runs the integration wrapper script using subprocess.run.
        The wrapper script will generate the output.json.
        It then opens and reads the contents of the expected_output.json and output.json files,
        and compares the contents using self.assertEqual to check if they are equal.
        """

        os.environ['INPUT_LOCATION'] = "input.json"
        os.environ['OUTPUT_LOCATION'] = "output.json"
        os.environ['RELEASE_URL'] = "http://localhost:5516"

        subprocess.run(["python", "-m", "digitalai.release.integration.wrapper"])

        with open('expected_output.json', 'r') as json_file:
            expected_output = json.load(json_file)

        with open('output.json', 'r') as json_file:
            actual_output = json.load(json_file)

        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()

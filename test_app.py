import unittest

from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # create an application context for testing
        self.ctx = app.app_context()
        # push the context onto the application stack
        self.ctx.push()
        # create a test client for the application
        self.client = app.test_client()

    def tearDown(self):
        # pop the application context from the application stack
        self.ctx.pop()

    def test_home(self):
        # simulate a POST request to the 'index' route with form data
        response = self.client.post(
            '/index',
            data=dict(content='go walking', degree='important'),
            follow_redirects=True
        )
        # assert that the response status code is 200

        # simulate a GET request to the 'index' route with query string parameters
        assert self.client.get('/index', query_string=dict(content='go walking', degree='important'))


if __name__ == "__main__":
    unittest.main()
import unittest
from src.remote_circles_storage import RemoteCirclesStorage


class TestRemoteCirclesStorage(unittest.TestCase):

    # @classmethod
    def setUp(self):
        self.remote_storage = RemoteCirclesStorage('http://localhost:5000')

    def test_put(self):
        result = self.remote_storage.put(
            'qltest.txt', 'C:/Git/qltest.txt', '1', '1', '1')
        self.assertIn('File uploaded with ID', result)

    def test_download(self):
        result = self.remote_storage.download(
            'qltest.txt', '1', '1', 'C:/test/')
        self.assertIn('File downloaded to C:/test/', result)


if __name__ == '__main__':
    unittest.main()

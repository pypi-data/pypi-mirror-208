import unittest
import shutil
from pathlib import Path
from github_downloader import GithubDownloader


class TestGithubDownloader(unittest.TestCase):
    def setUp(self):
        # This is the URL of the repository we'll use for testing
        self.repo_url = 'https://github.com/pippidis/github_downloader_testing.git'
        self.file_path = 'README.md' # This is a file in the repository
        self.folder_path = 'test_folder' # This is a folder in the repository
        self.folder_content_file_name = 'test_file.txt' # The name of the file in the test folder

        # Create a temporary directory for downloads
        self.tmpdir = 'XXXX__temp_dir___XXXX' # Given a recognicable name
        Path(self.tmpdir).mkdir(exist_ok=True)

    def test_download_file(self):
        GithubDownloader.download_file(self.repo_url, self.file_path, self.tmpdir, logging=False) # Download the file
        downloaded_file = Path(self.tmpdir) / self.file_path # Get the full path of the downloaded file
        self.assertTrue(downloaded_file.exists()) # Assert that the file was downloaded

    def test_download_folder(self):
        GithubDownloader.download_folder(self.repo_url, self.folder_path, self.tmpdir, include_subfolders=True, logging=False) # Download the folder
        downloaded_file = Path(self.tmpdir) / self.folder_content_file_name # Get the full path of the downloaded folder
        self.assertTrue(downloaded_file.exists()) # Assert that the folder was downloaded

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.tmpdir)


if __name__ == '__main__':
    unittest.main()
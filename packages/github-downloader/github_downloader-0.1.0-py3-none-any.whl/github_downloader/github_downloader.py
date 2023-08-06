import git
from pathlib import Path
import shutil
import tempfile
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GithubDownloader:
    @staticmethod
    def _clone_repo_to_tempdir(repo_url: str, logging: bool=True) -> str:
        """
        Clone a GitHub repository to a temporary directory and return the path to the directory.

        :param repo_url: The URL of the GitHub repository.
        :param logging: Whether to logg with the logging package or not. Default is True.

        :return: The path to the temporary directory where the repository was cloned.
        """
        # Create a temporary directory
        tmpdirname = tempfile.mkdtemp()
        if logging: logger.info(f'Created temporary directory {tmpdirname}')

        # Clone the repository
        repo = git.Repo.clone_from(repo_url, tmpdirname)
        if logging: logger.info(f'Cloned repository {repo_url} to {tmpdirname}')

        return tmpdirname

    @staticmethod
    def download_file(repo_url: str, file_path: str, local_dir: Optional[str] = None, logging: bool = True) -> None:
        """
        Clone a GitHub repository, copy a specific file to a local directory, and delete the cloned repository.

        :param repo_url: The URL of the GitHub repository.
        :param file_path: The path of the file in the repository.
        :param local_dir: The local directory where the file will be copied.
            If not provided, the file will be copied to the current directory.
        :param logging: Whether to log with the logging package or not. Default is True.
        """
        # If local directory is not provided, set it as the current directory
        if local_dir is None:
            local_dir = '.'

        try:
            # Clone the repository to a temporary directory
            tmpdirname = GithubDownloader._clone_repo_to_tempdir(repo_url)

            # Get the path of the file in the cloned repository
            file_path_in_repo = Path(tmpdirname) / file_path

            # Get the path of the local directory
            local_dir_path = Path(local_dir)

            # Create the local directory if it doesn't exist
            local_dir_path.mkdir(parents=True, exist_ok=True)

            # Get the destination file path in the local directory
            destination_file_path = local_dir_path / Path(file_path).name

            # Copy the file to the local directory
            shutil.copy2(file_path_in_repo, destination_file_path)

            if logging: logger.info(f'Copied {file_path} to {destination_file_path}')
        except Exception as e:
            if logging: logger.error(f'Failed to download {file_path} from {repo_url}. Error: {e}')

    @staticmethod
    def download_folder(repo_url: str, folder_path: str, local_dir: Optional[str] = None, include_subfolders: bool = True, logging: bool=True) -> None:
        """
        Clone a GitHub repository, copy the contents of a specific folder (including subdirectories, if specified) 
        to a local directory, maintaining the directory structure, and delete the cloned repository.

        :param repo_url: The URL of the GitHub repository.
        :param folder_path: The path of the folder in the repository.
        :param local_dir: The local directory where the contents of the folder will be copied.
            If not provided, a directory with the same name as the folder in the repository will be created in the current directory.
        :param include_subfolders: Whether to include subdirectories in the download. Default is True.
        :param logging: Whether to logg with the logging package or not. Default is True.
        """
        # If local directory is not provided, create a directory with the same name as the folder in the repository
        if local_dir is None:
            local_dir = folder_path.split('/')[-1]

        try:
            # Clone the repository to a temporary directory
            tmpdirname = GithubDownloader._clone_repo_to_tempdir(repo_url)

            # Get the path of the folder in the cloned repository
            folder_path_in_repo = Path(tmpdirname) / folder_path

            # Get the path of the local directory
            local_dir_path = Path(local_dir)

            # Use a different glob pattern depending on whether subdirectories should be included
            glob_pattern = '**/*' if include_subfolders else '*'

            # Iterate over all files and directories in the folder and its subdirectories
            for file_path in folder_path_in_repo.glob(glob_pattern):
                # Get the path of the file or directory relative to the folder in the repository
                relative_path = file_path.relative_to(folder_path_in_repo)

                # Append the relative path to the local directory path to maintain the directory structure
                local_file_path = local_dir_path / relative_path

                # Create the parent directory of the local file or directory
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                # If it's a file, copy it
                if file_path.is_file():
                    shutil.copy2(file_path, local_file_path)
                # If it's a directory, copy the entire directory tree
                elif include_subfolders:
                    shutil.copytree(file_path, local_file_path, dirs_exist_ok=True)
            if logging: logger.info(f'Copied the contents of {folder_path} to {local_dir}')
        except Exception as e:
            if logging: logger.error(f'Failed to download {folder_path} from {repo_url}. Error: {e}')

# github_downloader

A simple package for downloading files from github repos.

It is simple it: 
1. Clones the repo to a temporary folder
2. Copies what you want from the temp folder to your target
3. Deletes the temp folder. 

_NOTE_: I recomend not using it on very large repos.


## Usage examples: 

Download a single file: 
```python
from github_downloader import GithubDownloader
GithubDownloader.download_file('https://github.com/pippidis/github_downloader.git','github_downloader/__init__.py', '.')
```


Download a folder with subfolders: 
```python
from github_downloader import GithubDownloader
GithubDownloader.download_folder('https://github.com/pippidis/github_downloader.git','github_downloader', '.', include_subfolders=True)
```


from setuptools import setup, find_packages

setup(
    name='github_downloader',
    version='0.1.0',
    url='https://github.com/pippidis/github_downloader',
    author='Johannes Lorentzen',
    author_email='pippidis@gmail.com',
    description='A simple packace that lets you download files and folders from a github repo.',
    packages=find_packages(),    
    install_requires=[
        'gitpython', 'pathlib', 'shutil' , 'tempfile', 'typing'
    ],
)
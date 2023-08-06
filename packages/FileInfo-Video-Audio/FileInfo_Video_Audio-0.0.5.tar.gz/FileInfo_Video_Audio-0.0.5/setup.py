from setuptools import setup, find_packages
import os

requirements = os.popen("/usr/local/bin/pipreqs main --print").read().splitlines()
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='FileInfo_Video_Audio',
    version='0.0.5',
    author='Sridhar',
    author_email='dcsvsridhar@gmail.com',
    description="In this tool is help to get the properties of the Audio and Video files",
    packages=find_packages(),
    url='https://git.selfmade.ninja/SRIDHARDSCV/collage_sem_4_python_project_cli_file_details',
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'GetFileinfo_Audio_Video=source.main:main',
        ],
    },
)

from setuptools import find_packages, setup
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='scrapere',
    packages=find_packages(),
    version='0.2.3',
    description='Small set of my web scraping python tools',
    author='vPere',
    license='MIT',
    readme='README.md',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'colorama',
        'emoji'
    ],
    include_package_data=True,
    package_data={'': ['*.txt']},
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vPere/scrapere'
)

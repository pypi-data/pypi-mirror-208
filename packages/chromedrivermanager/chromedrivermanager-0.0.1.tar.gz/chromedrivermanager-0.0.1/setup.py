from setuptools import setup, find_packages
# import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.1'
DESCRIPTION = 'A simple Python library that check, update or download chrome driver'
LONG_DESCRIPTION = 'A package that allows to manage chromedriver'

# Setting up
setup(
    name="chromedrivermanager",
    version=VERSION,
    author="Joshi Hrithik V",
    author_email="hrithikjoshi987@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests', 'pypiwin32', 'pywin32'],
    keywords=['python', 'chrome', 'chromedriver', 'selenium', 'webdriver', 'driver'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
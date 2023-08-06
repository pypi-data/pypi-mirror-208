from setuptools import setup, find_packages, __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kwamehealthtoolboxpublic",
    version="1.3.2",
    author="Panashe Madzudzo",
    author_email="admin@kwame.health",
    description="Toolbox with custom functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kwame-Health/khtoolbox",
    project_urls = {
        "Bug Tracker": "https://github.com/Kwame-Health/khtoolbox/issues"
    },
    packages=["kwamehealthtoolboxpublic"],
    install_requires=["requests", "urllib3", "twilio", "pytz", "boto3", "convertapi"],
)
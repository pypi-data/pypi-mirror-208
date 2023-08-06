from setuptools import setup, find_packages

setup(
    name="my-api-plugin",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["requests"],
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple API plugin with POST requests",
    url="https://github.com/yourusername/my_api_plugin",
)
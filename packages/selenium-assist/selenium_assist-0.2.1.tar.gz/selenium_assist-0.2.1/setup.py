import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="selenium_assist",
    version="0.2.1",
    author="Ivan Mičetić",
    author_email="ivan.micetic@gmail.com",
    description="Helper functions for selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivanmicetic/selenium-assist",
    project_urls={
        "Bug Tracker": "https://github.com/ivanmicetic/selenium-assist/issues"
    },
    license="MIT",
    packages=["selenium_assist"],
    install_requires=["selenium<4", "webdriver_manager", "urllib3<2"],
    keywords=["pypi", "selenium_assist"],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    download_url="https://github.com/ivanmicetic/selenium-assist/archive/refs/tags/v0.2.1.tar.gz"
)

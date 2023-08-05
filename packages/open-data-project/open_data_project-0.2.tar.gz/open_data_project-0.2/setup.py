from setuptools import setup, find_packages

setup(
    name = "open_data_project",
    version = "0.2",
    author = "Danail Dimov",
    author_email = "d.dimov62@gmail.com",
    description = "A Python package to retrieve the data for your open data portal and to launch the front-end structure for its website.",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ["beautifulsoup4",
                        "black",
                        "datefinder",
                        "Markdown",
                        "pandas==1.4.4",
                        "pytest==7.1.2",
                        "PyYAML==6.0",
                        "PyGithub",
                        "requests",
                        "flake8",
                        "validators",
                        "python-dateutil"
                        ],
    entry_points = {
        "console_scripts": [
        "odp=open_data_project.odp:main"
        ]
    }
)

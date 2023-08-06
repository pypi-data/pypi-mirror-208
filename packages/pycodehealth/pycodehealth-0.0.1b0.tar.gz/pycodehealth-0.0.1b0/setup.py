"""
Module to create the setup of the PyCodeHealth project
"""
import re
from pathlib import Path
from setuptools import setup, find_packages


def read_version() -> str:
    """Read the version from the given _version.py file

    Returns:
        - Version string

    Raise:
        - TypeError: If the version could not be find.
    """
    with open("pycodehealth/_version.py", "r", encoding="utf-8") as version_file:
        version_coincidence = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    # Now, check for the version coincidence
    if version_coincidence is None:
        raise TypeError("Couldn't find the version in the given file.")
    version = version_coincidence.group(1)
    # Return the version
    return version


__desc__ = "PyCodeHealth is a Python package for high-quality code maintenance, " +\
    "providing Static Code Analysis tools, automatic formatting, and a web-based " +\
    "Dashboard. It streamlines workflow and improves code quality, allowing users " +\
    "to choose their preferred linter, type checker, and formatting tool."
__long_desc__ = (Path(__file__).parent / "README.md").read_text()

setup(
    name='pycodehealth',
    version=read_version(),
    packages=find_packages(include=['pycodehealth']),
    author='Ricardo Leal',
    author_email='rick.leal420@gmail.com',
    maintainer='Ricardo Leal',
    maintainer_email='ricardo.lealpz@gmail.com',
    description=__desc__,
    long_description=__long_desc__,
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=[
        'click>=8.1', 'attrs>=22.1.0',
        'rich>=2.6', 'pylint>=2.15'
    ],
    include_package_data=True,
    python_requires=">=3.8, <4",
    entry_points="""
    [console_scripts]
    pycodehealth=pycodehealth.cli:tools
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development'
    ],
    project_urls={  # Optional
        "Bug Reports": "https://github.com/ricardoleal20/PyCodeHealth/issues",
    },
)

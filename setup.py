"""
setuptools develop is very good
"""

from setuptools import setup, find_packages  # or find_namespace_packages

setup(
    # ...
    packages=find_packages(
        # All keyword arguments below are optional:
        where='.',  # '.' by default
        include=['wg_config_manager'],  # ['*'] by default
        # exclude=['mypackage.tests'],  # empty by default
        package_data={"": ["default config.ini"]}
    ),
    include_package_data=True,
    # ...
)
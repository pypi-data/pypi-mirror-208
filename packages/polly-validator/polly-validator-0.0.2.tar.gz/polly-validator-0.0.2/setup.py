import pathlib

from setuptools import find_namespace_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent


def get_requirements():
    """Build the requirements list for this project"""
    requirements_list = []
    with open(HERE / 'requirements.txt') as reqs:
        for install in reqs:
            requirements_list.append(install.strip())
    return requirements_list


def get_packages_requirements():
    """Build the package & requirements list for this project"""
    reqs = get_requirements()
    packs = find_namespace_packages(include=['polly_validator',
                                             'polly_validator.*'])
    return packs, reqs


packages, requirements = get_packages_requirements()

setup(
    name='polly-validator',
    version='0.0.2',
    description='Data Validation Library',
    author='Sanchit Verma',
    long_description='# A data validation package to check the dataset level and sample level metadata for errors.',
    long_description_content_type='text/markdown',
    packages=packages,
    include_package_data=True,
    install_requires=requirements
)

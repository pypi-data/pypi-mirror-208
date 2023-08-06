import os
import logging as log
from shutil import rmtree
from setuptools import find_packages, setup
from distutils.command.clean import clean
from distutils.cmd import Command

package_name = 'gaiaFramework'
version = '1.0.16'
with open('requirements.txt') as f:
    required = f.read().splitlines()


class CleanCommand(clean):
    """
    Custom implementation of ``clean`` setuptools command."""

    def run(self):
        """After calling the super class implementation, this function removes
        the dist directory if it exists."""
        super().run()
        if os.path.exists(".eggs"):
            rmtree(".eggs")
        if os.path.exists(f"{package_name.replace('-', '_')}.egg-info"):
            rmtree(f"{package_name.replace('-', '_')}.egg-info")
        if os.path.exists("dist"):
            rmtree("dist")

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


dsp_files = package_files('gaiaframework/cli/tester/dsp')
extra_files = package_files('gaiaframework/cli/tester/deploy_files')
scripts_files = package_files('gaiaframework/cli/tester/scripts')
cloud_eval_extra_files = package_files('gaiaframework/cli/tester/cloud_eval')

setup(
    name=package_name,
    py_modules=['api_cli'],

    packages=find_packages(include=['gaiaframework*']),
    package_data={'': ['config.json', 'cors_allowed_origins.json', '.gitignore'] + extra_files + scripts_files + cloud_eval_extra_files + dsp_files},
    entry_points='''
        [console_scripts]
        gaia-cli=api_cli:cli
    ''',
    version=version,
    description='Data science framework library',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    # url='http://pypi.python.org/pypi/PackageName/',
    author='oribrau@gmail.com',
    license='MIT',
    install_requires=required,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    cmdclass={'clean': CleanCommand}
)

# commands
# for test -  python setup.py pytest
# for build wheel -  python setup.py bdist_wheel
# for source dist -  python setup.py sdist
# for build -  python setup.py build
# for install -  python setup.py install
# for uninstall - python -m pip uninstall gaiaframework
# for install - python -m pip install dist/gaiaframework-0.1.0-py3-none-any.whl

# deploy to PyPI
# delete dist and build folders
# python setup.py bdist_wheel
# python setup.py sdist
# python setup.py build
# twine upload dist/*
'''
    use
    1. python setup.py install
    2. gaia-cli g model new_model_name
    3. twine check dist/*
    4. twine upload --repository-url https://pypi.org/legacy/ dist/*
    4. twine upload dist/*
    
    pip install gaiaframework --index-url https://pypi.org/simple
    
    how to use
    
    pip install gaiaframework
    
    gaia-cli generate project my-new-model
'''

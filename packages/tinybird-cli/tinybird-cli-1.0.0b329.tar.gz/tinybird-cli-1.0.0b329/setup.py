from setuptools import setup, find_packages
import os

# https://stackoverflow.com/a/59969843
try:
    from pip._internal.req import parse_requirements
except ImportError:
    # pip < 10
    from pip.req import parse_requirements


def package_files(directory):
    paths = []
    for (path, _directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


def requirements_from_file(path):
    try:
        # Attemps to use the old API
        parsed_requirements = parse_requirements(path, session=False)
        requirements = [str(ir.req) for ir in parsed_requirements]
    except Exception:
        # Recreate the generator as we consumed one item from it
        parsed_requirements = parse_requirements(path, session=False)
        requirements = [str(ir.requirement) for ir in parsed_requirements]
    return requirements


extra_files = package_files('tinybird/templates') + package_files('tinybird/static') + \
    package_files('tinybird/default_tables') + package_files('tinybird/default_pipes') + \
    package_files('tinybird/sql') + package_files('tinybird/scripts')


setup(
    name='tinybird',
    version='1.0',
    description='tinybird',
    long_description='tinybird analytics',
    long_description_content_type='text/markdown',
    author='tinybird.co',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements_from_file('requirements.txt'),
    package_dir={"tinybird": "tinybird/"},
    package_data={
        # 'tinybird': ['../templates/*', '../static/*']
        'tinybird': extra_files
    },
    setup_requires=[
        'pytest-runner',
        'cffi==1.14.5'
    ],
    cffi_modules=[
        "tinybird/fast_leb128_build.py:ffibuilder",
        "tinybird/csv_importer_find_endline_build.py:ffibuilder"],  # "filename:global"
    extras_require={
        'test': requirements_from_file('requirements-test.txt') + requirements_from_file('requirements-linters.txt'),
        'deploy': requirements_from_file('requirements-deploy.txt'),
        'doc': requirements_from_file('requirements-doc.txt'),
        'devtools': requirements_from_file('requirements-devtools.txt'),
    },
    entry_points={
        'console_scripts': [
            'tinybird_server=tinybird.app:run',
            'tinybird_tool=tinybird.cli:cli',
            'tb=tinybird.tb_cli:cli',
            'colibri=tinybird.colibri.main:cli',
        ],
    }
)

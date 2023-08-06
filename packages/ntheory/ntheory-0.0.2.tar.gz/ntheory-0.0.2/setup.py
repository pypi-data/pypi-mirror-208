from setuptools import find_packages, setup

setup(
    name='ntheory',
    packages=find_packages(include=['ntheory']),
    version='0.1.0',
    description='My first Python library',
    author='Kasper Arfman',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.3.1'],
    test_suite='tests',
)

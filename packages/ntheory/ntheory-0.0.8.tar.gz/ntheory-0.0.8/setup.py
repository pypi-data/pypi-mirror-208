from setuptools import find_packages, setup

setup(
    name='ntheory',
    packages=find_packages(),
    version='0.0.8',
    description='My first Python library',
    author='Kasper Arfman',
    license='MIT',
    install_requires=[
        'numpy==1.24.3',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.3.1'],
    test_suite='tests',
)

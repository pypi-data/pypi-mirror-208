from setuptools import setup

setup(
    name='p_js_rs',
    version='0.0.1',
    description='A package for working with JSON files',
    author='Rajveer Singh',
    author_email='rajveersingh81248@gmail.com',
    packages=['p_js'],
    entry_points={
        'console_scripts': [
            'pjs = p_js.pjs:main',
        ],
    },
)

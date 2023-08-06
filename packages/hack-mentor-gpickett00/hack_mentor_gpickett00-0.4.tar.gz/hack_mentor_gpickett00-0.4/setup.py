from setuptools import setup, find_packages

setup(
    name='hack_mentor',
    version='0.4',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hack_mentor = hack_mentor.main:main',
        ],
    },

)

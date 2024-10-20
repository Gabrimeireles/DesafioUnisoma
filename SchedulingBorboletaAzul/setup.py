from setuptools import setup, find_packages

setup(
    name='desafio_unisoma',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'pulp',
        'streamlit'
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'desafio_unisoma=desafio_unisoma:main'
        ]
    }
)

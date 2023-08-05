from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="msqlpd",
    version="4.0.4",
    author="Moses Dastmard",
    description="return a path information",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'sqlalchemy',
        'pandas',
        'mysql-connector-python',
        'joblib',
    ]
)
from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='thelemic-date',
    version='5.93',
    description='A class for Thelemic date and time calculations.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Lilith Vala Xara',
    author_email='lvx@93.is',
    url='https://github.com/LilithXara/ThelemicDate',  # Add your project's GitHub repository URL
    project_urls={
        'Homepage': 'https://Thelema.Chat'  # Add your project's homepage URL
    },
    py_modules=['thelemic_date'],
    install_requires=[
        'flatlib',
        'geopy',
        'pytz',
        'timezonefinder',
    ],
)


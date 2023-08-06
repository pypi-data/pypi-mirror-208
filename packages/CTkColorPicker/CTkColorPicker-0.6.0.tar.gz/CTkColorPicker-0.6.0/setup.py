from setuptools import setup

def get_long_description(path):
    """Opens and fetches text of long descrition file."""
    with open(path, 'r') as f:
        text = f.read()
    return text

setup(
    name = 'CTkColorPicker',
    version = '0.6.0',
    description = "A modern color picker for customtkinter",
    license = "Creative Commons Zero v1.0 Universal",
    readme = "README.md",
    long_description = get_long_description('README.md'),
    long_description_content_type = "text/markdown",
    author = 'Akash Bora',
    url = "https://github.com/Akascape/CTkColorPicker",
    package_data = {'': ['*.png']},
    classifiers = [
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords = ['customtkinter', 'customtkinter-dialog', 'customtkinter-color-picker',
                'customtkinter-colour-picker', 'customtkinter-color', 'customtkinter-color-chooser',
                'color-picker', 'python-color-picker'],
    packages = ["CTkColorPicker"],
    install_requires = ['customtkinter', 'pillow'],
    dependency_links = ['https://pypi.org/project/customtkinter/', 'https://pypi.org/project/Pillow/'],
    python_requires = '>=3.6',
)

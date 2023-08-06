from setuptools import setup

def get_long_description(path):
    """Opens and fetches text of long descrition file."""
    with open(path, 'r') as f:
        text = f.read()
    return text

setup(
    name = 'tknodesystem',
    version = '0.1',
    description = "Simple visual node system (DAG) with tkinter!",
    license = "MIT",
    readme = "README.md",
    long_description = get_long_description('README.md'),
    long_description_content_type = "text/markdown",
    author = 'Akash Bora',
    url = "https://github.com/Akascape/TkNodeSystem",
    package_data = {'': ['*.png']},
    classifiers = [
        "License :: OSI Approved :: MIT License ",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords = ['customtkinter', 'tkinter', 'tkinter-nodes',
                'tknodes', 'tkinter-DAG', 'node-system',
                'node-based-ui', 'tknodesystem', 'nodes'],
    packages = ["tknodesystem", "tknodesystem.grid_images"],
    install_requires = ['customtkinter'],
    dependency_links = ['https://pypi.org/project/customtkinter/'],
    python_requires = '>=3.6',
)

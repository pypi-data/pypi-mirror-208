from setuptools import setup, find_packages

# https://github.com/pypa/sampleproject/blob/main/setup.py
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name='africamonitor',
    version='0.1.2',
    description='An API providing access to a relational database with macroeconomic data for Africa.',
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",
    url='https://africamonitor.ifw-kiel.de/',
    author="Sebastian Krantz",
    author_email='sebastian.krantz@graduateinstitute.ch',
    # Classifiers help users find your project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Pick your license as you wish
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
    ],
    keywords='africa, macroeconomic, data, API',
    package_dir={"": "src"},  # Optional
    py_modules=["africamonitor"],
    python_requires=">=3.1",
    install_requires=['connectorx', 'pyarrow', 'polars'],
    license='GPL-3',
    # include_package_data=True,
    # package_data={'africamonitor': ['data/*.csv']}, # Using MANIFEST.in
    project_urls={  # Optional
        "Bug Reports": "https://github.com/IFW-Macro-Research-Group/africamonitor",
    },
)

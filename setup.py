from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# from calvincTools import (__version__, __author__, __email__, )
# sorry, build will fail with the above line, so manually set them here
__version__ = "1.6.3"
__author__ = "Calvin C"
__email__ = "calvinc404@gmail.com"

setup(
    name="calvincTools",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="A Python package for calvincTools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calvinc-org-10/calvincTools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Add your package dependencies here
        # e.g., "numpy>=1.20.0",
        "PySide6==6.10.1",
        "PySide6_Addons==6.10.1",
        "PySide6_Essentials==6.10.1",
        "typing_extensions==4.12.2",
        "et_xmlfile==2.0.0",
        "openpyxl==3.1.5",
        "qtawesome==1.4.0",
        "shiboken6==6.10.1",
        "SQLAlchemy==2.0.36",
        "sqlparse==0.5.3",
        "python-dateutil==2.9.0.post0",
        "tzdata==2024.2"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
)

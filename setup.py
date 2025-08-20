from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="data-platform",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modular data engineering platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/data-platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "docker>=6.1.0",
        "jsonschema>=4.0.0",
        "rich>=13.0.0",
        "inquirer>=3.1.0",
        "tabulate>=0.9.0",
        "jinja2>=3.1.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "platform=platform.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "platform": [
            "templates/*.yaml",
            "templates/*.yml",
            "configs/*.yaml",
        ],
    },
)

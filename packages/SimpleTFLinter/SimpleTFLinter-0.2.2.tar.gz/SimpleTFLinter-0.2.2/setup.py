from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="SimpleTFLinter",
    version="0.2.2",
    author="William Wang",
    author_email="williamwangatsydney@gmail.com",
    description="Simple Terraform Linter is a lightweight command-line tool for checking Terraform configuration files against custom rules. It supports input from Terraform folders or JSON files, with easy customization and extensibility through user-defined rules defined in YAML files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutomationLover/TerraformLinter",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["cli"],  # Include the cli.py module
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=requirements,  # Use the requirements loaded from requirements.txt
    entry_points={
        "console_scripts": [
            "simple_tf_linter=cli:main",
        ],
    },
)

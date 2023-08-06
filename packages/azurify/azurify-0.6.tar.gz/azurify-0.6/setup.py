from setuptools import find_packages, setup

with open("Readme.md", "r") as f:
    long_description = f.read()

setup(
    name="azurify",
    version="0.6",
    description="Access to Azure Storage/Secrets/Keyvault for Shopify Apps built with Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zinyosrim/azurify",
    author="Zin Yosrim",
    author_email="zinyosrim@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "pandas",
        "StrEnum",
        "azure-identity",
        "azure-keyvault-secrets",
        "azure-mgmt-keyvault",
        "azure-mgmt-resource",
        "azure-storage-blob",
    ],
    extras_require={"dev": ["unitest", "twine"]},
    zip_safe=False,
    python_requires=">=3.9",
)

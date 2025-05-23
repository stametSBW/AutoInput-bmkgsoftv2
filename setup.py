from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="autoinput-bmkgsoftv2",
    version="0.1",
    author="Zulkifli Ramadhan",
    author_email="zulkiflirmdn@gmail.com",
    description="Automated data input App for BMKG Satu platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bmkg-autoinput",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bmkg-autoinput=ui.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bmkg_autoinput": ["config/*.yaml"],
    },
) 
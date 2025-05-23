from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="autoinput-bmkgsoftv2",
    version="0.2.0",
    author="Zulkifli Ramadhan",
    author_email="zulkiflirmdn@gmail.com",
    description="Modern automated data input application for BMKG Satu platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AutoInput-BMKGsoftV2",
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
        "Topic :: Office/Business :: Automation",
        "Framework :: PyQt6",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bmkg-autoinput=src.ui.modern_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "autoinput_bmkgsoftv2": [
            "config/*.yaml",
            "assets/*.ico",
            "assets/*.png",
        ],
    },
) 
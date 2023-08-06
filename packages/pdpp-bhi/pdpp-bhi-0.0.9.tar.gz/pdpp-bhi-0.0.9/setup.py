from setuptools import setup, find_packages

setup(
    name="pdpp-bhi",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    version="0.0.9",
    license="MIT",
    description="PDPP - BHI",
    author="Dohoon Lee",
    author_email="dohlee.bioinfo@gmail.com",
    long_description_content_type="text/markdown",
    url="https://github.com/dohlee/pdpp",
    keywords=[
        "kaggle",
    ],
    install_requires=[
        "numpy",
        "pandas",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)

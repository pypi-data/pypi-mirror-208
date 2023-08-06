from setuptools import find_packages, setup


setup(
    name="cat_dog_lib",
    version="0.0.1",
    description="Mô tả ngắn",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description='Mô tả dài',
    long_description_content_type="text/markdown",
    url="https://github.com/anthule123/first_package_An",
    author="anthule123",
    author_email="lethithuan_t63@hus.edu.vn",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": ["pytest>=7.0",
                "twine>=3.4.2",]
        
    },
    python_requires=">=3.10",
)

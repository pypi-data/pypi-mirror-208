from setuptools import setup


setup(
    name="XMLAndJSONSerializer",
    version="0.1.0",
    description="Library for class and function serialization",
    author="Uladzislau",
    author_email="vladislav2256@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializers", "tests"],
    include_package_data=True,
    install_requires=["regex"]
)

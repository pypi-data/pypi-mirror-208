import setuptools

setuptools.setup(
    name="qqtest01",
    version=1.0,
    long_description="This is the homepage of our project",
    packages=setuptools.find_packages(exclude=["tests", "data"])
)

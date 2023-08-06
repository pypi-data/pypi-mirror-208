import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zypl_macro",
    version="1.0.0",
    author="Me",
    description="zypl.ai alternative data API interface lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                      
    python_requires='>=3.0',
    py_modules=["library"],
    install_requires=[
        'pandas>=1.5.3',
        'requests>=2.28.2']
)
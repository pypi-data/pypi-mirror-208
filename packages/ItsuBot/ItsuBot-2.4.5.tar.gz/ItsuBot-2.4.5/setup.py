import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="ItsuBot",
    version="2.4.5",
    author="Pirxcy",
    description="Async Tool For Uploading URL's To PirxcyPinger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pirxcypingerfinal.pirxcy1942.repl.co/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'aiohttp'
    ],
)

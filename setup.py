import setuptools 

with open('README.md', 'r') as f:
    long_description = f.read()
    
setuptools.setup(
    name = 'pcb-parser',
    version = '0.1.0.rc4',
    author = 'Changyun Choi',
    author_email = "cyun9601@gmail.com",
    description = "PCB Parser",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/cyun9601/PCB_Parser",
    package_dir={"": "src"},
    packages = setuptools.find_packages("src"),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.7.0',
)
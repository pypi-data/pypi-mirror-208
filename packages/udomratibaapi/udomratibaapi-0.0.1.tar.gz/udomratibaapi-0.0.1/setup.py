from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Fetch data from the UDOM ratiba website in a clean JSON format'
LONG_DESCRIPTION = ""
with open('readme.md') as rm:
    LONG_DESCRIPTION = rm.read()

# Setting up
setup(
    name="udomratibaapi",
    version=VERSION,
    author="Vincent Laizer",
    author_email="<laizercorp@gmail.com>",
    url="https://github.com/vincent-laizer/UDOM-Ratiba-API",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['udom', 'ratiba', 'api', 'python', 'udom api', 'ratiba api', 'udom python'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
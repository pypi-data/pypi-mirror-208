import setuptools

VERSION = '0.0.1'
DESCRIPTION = ''
LONG_DESCRIPTION = ''

# Setting up
setuptools.setup(
    name="doom_hello_henriq4",
    version=VERSION,
    author="Henrique GC",
    author_email="<henriq4net@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=setuptools.find_packages(),
    py_modules=["doom_hello_henriq4"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = ''
LONG_DESCRIPTION = ''

setup(
    name="escoffier",
    version=VERSION,
    author="epistoteles",
    author_email="<korbinian.koch@uni-hamburg.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

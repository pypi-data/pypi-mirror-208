from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Stock Market Trading Framework'
LONG_DESCRIPTION = 'A Framework for simple creation and deployment of trading strategies.'

# Setting up
setup(
    name="mktrader",
    version=VERSION,
    author="Matthew K Murphy (MatthewKurtis)",
    author_email="<mkmurphy526@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'websocket-client'
        ],
    keywords=['python', 'trading', 'stock', 'market'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
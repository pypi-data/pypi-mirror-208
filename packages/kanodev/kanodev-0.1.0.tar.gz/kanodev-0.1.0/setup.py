from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'Use natural language to create a fully functional, tested and deployed cloud infrastructure with a single command!'
LONG_DESCRIPTION = 'This project streamlines the creation and deployment of cloud infrastructure. Simply describe your problem using natural language, and the system will automatically build, test and deploy a cloud architecture based on your prompt.'

# Setting up
setup(
    name="kanodev",
    version=VERSION,
    author="KanoScale",
    author_email="<info@kanoscale.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kanodev = kanodev.kanodev:main',
        ],
    },
    install_requires=['openai', 'boto3', 'localstack', 'python-terraform'],
    keywords=['GPT', 'AWS', 'Cloud', 'Infrastructure', 'Natural Language', 'OpenAI', 'KanoScale', 'KanoDev', 'Kano'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
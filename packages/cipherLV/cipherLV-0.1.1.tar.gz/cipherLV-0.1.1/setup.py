from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.1'
DESCRIPTION = 'Description: LV cipher is used for encrypting and decrypting with symmetric key'
#LONG_DESCRIPTION = 'Long Description: LV Cipher is used for encrypting and decrypting with symmetric key'

# Setting up
setup(
    name="cipherLV",
    version=VERSION,
    author="sarath babu",
    author_email="babusarath05@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    #install_requires=['sklearn','pandas'],
    keywords=['python', 'encryption','decryption','cryptography'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

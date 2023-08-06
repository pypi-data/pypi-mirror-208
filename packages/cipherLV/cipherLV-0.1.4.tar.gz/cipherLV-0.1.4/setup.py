from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


# Setting up
setup(
    name="cipherLV",
    version="0.1.4",
    author="sarath babu",
    author_email="sarathbabu.karunanithi@latentview.com",
    description='Description: LV cipher is used for encrypting and decrypting with symmetric key',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    py_modules=['cipherLV'],
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

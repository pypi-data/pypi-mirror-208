from setuptools import setup, find_packages

setup(
    name='characterai',
    version='0.4.0',
    author='kramcat',
    description='An unofficial API for character.ai for Python',
    url='https://github.com/kramcat/characterai',
    packages=find_packages(),
    install_requires=["playwright>=1.32.1"],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
)
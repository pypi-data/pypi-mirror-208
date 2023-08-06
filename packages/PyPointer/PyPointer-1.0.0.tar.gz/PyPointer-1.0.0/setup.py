from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='PyPointer',
    version='1.0.0',
    packages=['Pointer'],
    url='https://github.com/0gl20shk0sbt36/Pointer/tree/pypi',
    license='MIT License',
    author='0gl20shk0sbt36',
    author_email='3503973883@qq.com',
    description='A pointer to python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)

from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='checkify',
    version='0.6',
    packages=['checkify'],
    install_requires=[
        'openai'
    ],
    author="Tripathi Aditya Prakash",                     # Full name of the author
    description="Python package that utilizes the power of the GPT API to provide comprehensive code analysis and assistance. It helps you identify errors in code, explains the code logic, and offers valuable suggestions for improvement.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aditya0072001/checkify',
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    project_urls={
        'Download Statistics': 'https://pepy.tech/project/checkify/month',
    },
)

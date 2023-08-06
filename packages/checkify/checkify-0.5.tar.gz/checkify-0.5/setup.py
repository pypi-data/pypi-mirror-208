from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='checkify',
    version='0.5',
    packages=['checkify'],
    install_requires=[
        'openai'
    ],
    author="Tripathi Aditya Prakash",                     # Full name of the author
    description="Python package that utilizes the GPT API to check for errors in code and explain the code.",
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

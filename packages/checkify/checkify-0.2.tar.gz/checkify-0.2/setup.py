from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='checkify',
    version='0.2',
    packages=['checkify'],
    install_requires=[
        'openai'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aditya0072001/checkify',
    project_urls={
        'Download Statistics': 'https://pepy.tech/project/checkify/month',
    },
)

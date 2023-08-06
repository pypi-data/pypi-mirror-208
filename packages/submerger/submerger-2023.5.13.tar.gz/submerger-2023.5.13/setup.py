from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
  long_description = fh.read()

setup(
    author='Andrii Valiukh',
    author_email='andrii.valiukh0@gmail.com',
    description='Subtitle merging tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='submerger',
    version='2023.05.13',
    url='https://gitlab.com/andr1i/submerger',
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={'dev': [
        'mypy',
        'pylint',
    ]},
    scripts=['bin/submerge'],
)

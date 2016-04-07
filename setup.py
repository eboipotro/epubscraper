from setuptools import setup

setup(
    name='epubscraper',
    version='1.3.6',
    description='Post generator for eboipotro.github.io',
    author='Utsob Roy',
    author_email='uroybd@gmail.com',
    url='https://eboipotro.github.io/',
    py_modules = ['epubscraper'],
    install_requires=[
        'xmltodict',
        'pillow'
      ],
)

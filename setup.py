from setuptools import setup

setup(
    name='epubscraper',
    version='0.99',
    description='Post generator for eboipotro.github.io',
    author='Utsob Roy',
    author_email='uroybd@gmail.com',
    url='https://eboipotro.github.io/',
    py_modules = ['epubscraper'],
    install_requires=[
          'xmltodict',
      ],
)

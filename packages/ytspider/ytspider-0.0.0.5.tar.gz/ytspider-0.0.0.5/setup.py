
from setuptools import setup, find_packages


setup(
    name='ytspider',
    description="YouTube scraper, videos, channels, playlists, comments and transcriptions",
    version='0.0.0.5',
    license='MIT',
    author="Zeyad Khalid",
    maintainer_email='zeyad.khalid@must.edu.eg',
    author_email='zeyadpro99@gmail.com',
    package_dir={"ytspider":"src"},
    packages=find_packages(),#["ytspider","ytspider.utils"],
    py_modules=["ytspider.py"],
    url='https://github.com/zementalist',
    keywords='web crawling youtube scraping api',
    install_requires=[
          'requests',
          'bs4',
      ],
)
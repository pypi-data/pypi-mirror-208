from setuptools import setup, find_packages

setup(
    name="t4flib",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        'google-cloud-bigquery'
        ,'google-cloud-storage'
        ,'colorama'
        ,'pandas'
        ,'google-auth'
    ],
    author="Corentin DEVROUETE",
    author_email="cdevrouete@advanced-schema.com",
    description="Librairie de fonction utiles pour T4F",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8"
    ],
)

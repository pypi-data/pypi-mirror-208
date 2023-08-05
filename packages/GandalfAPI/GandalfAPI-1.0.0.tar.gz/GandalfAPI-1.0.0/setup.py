from setuptools import setup, find_packages

setup(
    name="GandalfAPI",
    version="1.0.0",
    description="A Python SDK for accessing The Lord of the Rings movie API",
    author="Aleem Saleem",
    author_email="mraleemsaleem@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="lord-of-the-rings movie api sdk",
)

from setuptools import setup

setup(
    name="cnki_html2json",
    author = "WangK2",
    author_email = "kw221225@gmail.com",
    version="0.1.9",
    description="A package to convert cnki html to json",
    long_description = open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords = ["cnki","text-structure","crawler"],
    license="MIT",
    url="https://github.com/doublessay/cnki-html2json",
    packages=["cnki_html2json"],
    python_requires=">=3.8.0",
    install_requires=[
        "selenium",
        "lxml",
        "opencv-python",
        "numpy",
        "loguru"],
    
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "cnki-crawler = cnki_html2json.cli:main",
        ]
    },

)
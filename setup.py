from setuptools import setup, find_packages

setup(
    name="md2gost",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-docx>=0.8.11",
        "marko>=2.0.0",
        "docxcompose>=1.4.0",
        "freetype-py>=2.4.0",
        "pillow>=10.0.0",
        "matplotlib>=3.7.2",
        "requests>=2.31.0",
        "latex2mathml>=3.76.0",
        "pygments>=2.16.1",
    ],
    package_data={
        "md2gost": ["Template.docx"],
    },
    include_package_data=True,
)


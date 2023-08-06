from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_img",
    version="0.0.3",
    author="Flayson Junio Pereira Santos",
    author_email="flaysonemail@gmail.com",
    description="My short description",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FlaysonSantos/",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
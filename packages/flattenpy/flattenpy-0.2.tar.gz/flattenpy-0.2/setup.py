from setuptools import setup

version = 0.2

try:
    with open("requirements.txt", "r") as f:
        required = f.read().split("\n")
except FileNotFoundError:
    required = []

setup(
    name="flattenpy",
    version=version,
    description="Flatten python scripts into a single file",
    author="Illia Ovcharenko",
    author_email="elijah.ovcharenko@gmail.com",
    packages=["flattenpy"],
    python_requires=">=3.7",
    install_requires=required,
    entry_points = {
        "console_scripts": ["flattenpy=flattenpy:cli"],
    }
)

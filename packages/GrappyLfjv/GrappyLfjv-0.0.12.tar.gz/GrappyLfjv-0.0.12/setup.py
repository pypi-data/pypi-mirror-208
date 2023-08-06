from setuptools import setup

setup(
    name= "GrappyLfjv",
    version= "0.0.12",
    description= "Simplification de la création de graphiques avec matplotlib",
    py_modules=["grappy"],
    package_dir={"": "src"},
    install_requires = [
        "matplotlib > 3.0"
    ],
    url="https://github.com/Benjamin-Trevian/Grappy",
    author="Benjamin Trévian",
    author_email="benjamin.trevian@hotmail.com",
)
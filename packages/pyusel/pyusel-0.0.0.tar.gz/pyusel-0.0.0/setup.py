from setuptools import setup

with open("README.md", 'r') as f:
    readme = f.read()

# run setup tools
setup(
    name="pyusel",
    description="Ultrasound Elasticity Imaging Toolkit",
    author="Wren Wightman",
    author_email="wew12@duke.edu",
    long_description=readme,
    install_requires=["pyusel-dispest"],
    version="0.0.0"
)
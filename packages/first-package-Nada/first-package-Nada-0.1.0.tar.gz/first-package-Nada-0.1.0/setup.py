from setuptools import setup

setup(
    name="first-package-Nada",
    version="0.1.0",
    author="Nada",
    author_email="nada_fhn24@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="my first package"
)

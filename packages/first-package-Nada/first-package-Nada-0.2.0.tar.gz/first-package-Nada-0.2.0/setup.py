from setuptools import setup
from pathlib import Path

d = Path(__file__).parent
description = (d / "README.md").read_text()

setup(
    name="first-package-Nada",
    version="0.2.0",
    author="Nada",
    author_email="nada_fhn24@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="my first package",
    long_description=description,
    long_description_content_type="text/markdown"
)

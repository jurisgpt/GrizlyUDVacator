from setuptools import find_packages, setup

setup(
    name="GrizlyUDVacator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "grizly = cli.main:main",
        ],
    },
)

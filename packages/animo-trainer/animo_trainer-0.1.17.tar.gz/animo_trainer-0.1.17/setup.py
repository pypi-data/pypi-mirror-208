from setuptools import setup
from pathlib import Path

LONG_DESCRIPTION = Path.joinpath(Path(__file__).parent, "README.md").read_text()

exec(open('animo_trainer/version.py').read())
setup(
    name="animo_trainer",
    version=__version__, #type: ignore
    description="Animo Trainer",
    long_description=LONG_DESCRIPTION,
    license_files = ('LICENSE.txt',),
    license="Copyright (c) 2023 Transitional Forms Inc. All Rights Reserved.",
    author="Transitional Forms",
    author_email="dante@transforms.ai",
    url="https://transforms.ai/",
    packages=['animo_trainer'],
    include_package_data=True,
    python_requires=">=3.9,<3.10",
    entry_points={
        "console_scripts": [
            "animo-learn=animo_trainer.main:main",
        ],
    },
    install_requires = [
        "protobuf==3.20",
        "mlagents==0.30.0",
        "pythonnet==3.0.1",
        "torch==1.11.0",
        "psutil"
    ]
)

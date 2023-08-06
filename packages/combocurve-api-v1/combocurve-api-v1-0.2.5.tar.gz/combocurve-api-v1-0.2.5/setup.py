from setuptools import setup

setup(
    install_requires=[
        "cffi==1.15.1",
        "cryptography==40.0.2",
        "dataclasses==0.6; python_version == '3.6'",
        "pycparser==2.21",
        "pyjwt[crypto]==2.7.0",
    ],
    dependency_links=[],
)

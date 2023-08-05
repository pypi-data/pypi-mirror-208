from setuptools import setup, find_packages

setup(
    name="pyshuttlis",
    version="0.1.56",
    description="Utilities",
    url="https://github.com/shuttl-tech/pyshuttlis",
    author="Shuttl",
    author_email="sherub.thakur@shuttl.com",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=["pytz", "voluptuous", "ddtrace>=1.6.0", "sentry_sdk>=0.14.4"],
    extras_require={
        "test": ["pytest", "pytest-runner", "pytest-cov", "pytest-pep8"],
        "dev": ["flake8"],
    },
)

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pts_fault_injection",
    version="0.0.8",
    author="Pass testing Solutions GmbH",
    description="Fault Injection box Diagnostics package Diagnostic Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="shuparna@pass-testing.de",
    url="https://gitlab.com/pass-testing-solutions/pts-fault-injection-box",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    py_modules=["pts_fault_injection"],
    install_requires=['python-can==4.0.0', 'dash==2.5.1', 'cantools==37.0.7', 'tabulate==0.8.10', 'uptime==3.0.1',
                      'pyserial==3.5'],
    packages=find_packages(include=['pts_fault_injection']),
    include_package_data=True,
)

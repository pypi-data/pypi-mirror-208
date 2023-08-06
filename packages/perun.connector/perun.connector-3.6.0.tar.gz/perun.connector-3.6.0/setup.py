import setuptools

setuptools.setup(
    name="perun.connector",
    python_requires=">=3.9",
    url="https://gitlab.ics.muni.cz/perun-proxy-aai/python/perun-connector.git",
    description="Module for communication with Perun IAM system",
    packages=setuptools.find_namespace_packages(include=["perun.*"]),
    install_requires=[
        "setuptools",
        "urllib3>=1.26.9,<2",
        "python-dateutil>=2.8.2,<3",
        "PyYAML>=6.0,<7",
        "ldap3>=2.9.1,<3",
        "jsonpatch>=1.22,<2",
    ],
)

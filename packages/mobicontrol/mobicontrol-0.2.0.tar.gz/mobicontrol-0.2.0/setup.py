from setuptools import setup

setup(
    name="mobicontrol",
    version="0.2.0",
    packages=["mobicontrol", "mobicontrol.scripts"],
    include_package_data=True,
    install_requires=["Click", "requests"],
    entry_points={"console_scripts": ["mobicontrol = mobicontrol.main:mobicontrol"]},
)

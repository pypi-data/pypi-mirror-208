from setuptools import setup, find_packages

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name = "phase-o-matic",
    version = "0.0.3",
    license='MIT',
    author="Zachary Keskinen",
    author_email='zachkeskinen@gmail.com',
    description = "InSAR Atmospheric Delay Corrections with ERA5",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/ZachKeskinen/phase-o-matic',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "phase_o_matic"},
    packages = find_packages(where="phase_o_matic"),
    python_requires = ">=3.6",
    keywords='phase-o-matic',
    install_requires=[
          'numpy',
          'pandas',
          'xarray',
          'rioxarray',
          'shapely',
          'cdsapi',
          'scipy'
      ],
)

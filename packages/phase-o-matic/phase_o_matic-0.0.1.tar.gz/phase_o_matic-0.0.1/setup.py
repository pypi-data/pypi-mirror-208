from setuptools import setup, find_packages


setup(
    name='phase_o_matic',
    version='0.0.1',
    license='MIT',
    author="Zachary Keskinen",
    author_email='zachkeskinen@gmail.com',
    packages=find_packages('phase_o_matic'),
    package_dir={'': 'phase_o_matic'},
    url='https://github.com/ZachKeskinen/phase-o-matic',
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
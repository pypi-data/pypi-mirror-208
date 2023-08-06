from setuptools import setup, find_packages


setup(
    name="lexisnexisapi",
    version='2.0.45',
    license='MIT',
    author="Robert Cuffney",
    author_email='robert.cuffney@lexisnexis.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    url='',
    keywords='example project',
    install_requires=[],
     

)
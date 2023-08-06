from setuptools import setup

setup(
    name='first-package-Ionel-Ujica',
    version='0.1.0',
    author='Ionel',
    author_email='ionelujica@yahoo.com',
    packages=['my_own_package'],
    package_dir={'':'src'},
    include_package_data=True,
    description='My first package'
)
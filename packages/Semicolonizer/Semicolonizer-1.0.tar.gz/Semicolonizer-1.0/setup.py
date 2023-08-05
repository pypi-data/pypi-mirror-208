from setuptools import setup, find_packages

install_requires = [
    "pynput==1.7.6",
    "setuptools==65.5.0",
    "win10toast==0.9",
]
setup(
    name='Semicolonizer',
    version='1.0',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Mobin',
    author_email='12345mobin12345@gmail.com',
    description='a tool for semicolonize php files!',
    ext_package="Semicolonizer",

)

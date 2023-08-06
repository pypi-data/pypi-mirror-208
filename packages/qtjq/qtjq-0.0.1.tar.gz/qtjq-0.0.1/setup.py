from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'qtjq/version.py'), 'r') as f:
    exec(f.read())


setup(
    name='qtjq',
    version=__version__,
    url='',
    license='',
    author='Andrew Hu',
    author_email='AndrewWeiHu@gmail.com',
    description='Quant Trading Related',
    packages=find_packages(exclude=['backup']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'qtc>=0.0.3'
    ],
    tests_require=[
        'pytest'
    ],
)

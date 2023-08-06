from setuptools import setup, find_packages

setup(
    name='ufusion',
    version='1.0.1',
    description='',
    author='f09l',
    author_email='fostn.contact@gmail.com',
    packages=find_packages(),
    install_requires=['requests','colorama','blessed'],
    entry_points={
        'console_scripts': [
            'fusion=Fusion.Fusion:main',
        ],
    },
)

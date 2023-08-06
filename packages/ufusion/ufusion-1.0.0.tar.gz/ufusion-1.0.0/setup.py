from setuptools import setup

setup(
    name='ufusion',
    version='1.0.0',
    description='',
    author='f09l',
    author_email='fostn.contact@gmail.com',
    packages=['Fusion'],
    install_requires=['requests','colorama','blessed'],
    entry_points={
        'console_scripts': [
            'fusion=Fusion.Fusion:main',
        ],
    },
)

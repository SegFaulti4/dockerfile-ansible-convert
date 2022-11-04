import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

install_requires = (here / 'requirements.txt').read_text(encoding='utf-8').splitlines()

setup(
    install_requires=install_requires,
    name='dockerfile_ansible_convert',
    entry_points={
        'console_scripts': [
            'd2a-convert = main:main'
        ],
    }
)
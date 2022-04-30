import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

install_requires = (here / 'requirements.txt').read_text(encoding='utf-8').splitlines()

setup(
    install_requires=install_requires,
    name='docker2ansible',
    entry_points={
        'console_scripts': [
            'docker2ansible = docker2ansible.docker2ansible:entrypoint'
        ],
    }
)
from pathlib import Path
from setuptools import setup
import pkg_resources

from bsc_utils import __version__


def parse_requirements(filename: str) -> list:
    with Path(filename).open() as f:
        install_requires = [
            str(requirement)
            for requirement in pkg_resources.parse_requirements(f)
        ]

    return install_requires


setup(
    name='bsc_utils',
    version=__version__,
    description='Util Functions for BSC Quants',
    author='Trung Dang',
    author_email='trungd@bsc.com.vn',
    maintainer='Trung Dang',
    maintainer_email='trungd@bsc.com.vn',
    url='https://github.com/dang-trung/bsc-utils',
    license='MIT',
    packages=['bsc_utils'],
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

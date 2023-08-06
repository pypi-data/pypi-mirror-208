import warnings

from setuptools import find_packages
from setuptools import setup

VERSION = "15.0.4"  # WARNING: build script replace 15.0.4 with an actual three-decimal version using `sed` in file!

if not VERSION or VERSION == "15.0.4":
    warnings.warn(f'Invalid package version "{VERSION}". If that is NOT a local debug installation you must replace '
                  f'VERSION with a valid value or provide 15.0.4 environment variable for the build script.')

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pytpu',
    packages=find_packages(exclude='pytpu_tests'),
    version=VERSION,
    author="IVA-Tech",
    author_email="info@iva-tech.ru",
    description="TPU Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://git.mmp.iva-tech.ru/tpu_sw/iva_tpu_sdk",
    install_requires=[
        'numpy',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-xdist',
            'pytest-cov',
            'Pillow',
            'flake8',
            'mypy',

            # Documentation
            'sphinx',  # docs engine
            'sphinx-click',  # to automatically document click-based applications
            'sphinx-rtd-theme',  # ReadTheDocs theme for html formatting
            'sphinxcontrib-plantuml',  # UML diagrams support

            'tpu-tlm-is~=0.3.0.1'  # To test RAW mode
        ],
    },
    zip_safe=False,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'run_get_fps = pytpu.scripts.run_get_fps:main',
            'pyrun_tpu = pytpu.scripts.pyrun_tpu_cli:main'
        ]
    },
)

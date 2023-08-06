#!/usr/bin/env python

from pathlib import Path

from setuptools import find_packages, setup

entry_points = {
    'console_scripts': [
        'eossr-zip-repository = eossr.scripts.zip_repository:main',
        'eossr-codemeta2zenodo = eossr.scripts.eossr_codemeta2zenodo:main',
        'eossr-upload-repository = eossr.scripts.eossr_upload_repository:main',
        'eossr-check-connection-zenodo = eossr.scripts.check_connection_zenodo:main',
        'eossr-metadata-validator = eossr.scripts.eossr_metadata_validator:main',
        'eossr-zenodo-metadata-validator = eossr.scripts.eossr_zenodo_validator:main',
    ]
}


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='eossr',
    description="ESCAPE OSSR library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires="setuptools_scm",
    install_requires=[
        "requests>=2.25.0,<3.0",
        "markdown>=3.3.6,<4.0",
        "pandas",
        "remotezip==0.9.3",
        "semver>=2,<3",
        "jsonschema",
        "jsonref",
    ],
    extras_require={'tests': ['pytest', 'pytest-cov'], 'extras': ['pre-commit']},
    packages=find_packages(exclude="eossr._dev_version"),
    scripts=[],
    tests_require=['pytest'],
    author='Thomas Vuillaume, Enrique Garcia',
    author_email='vuillaume@lapp.in2p3.fr',
    url='https://gitlab.in2p3.fr/escape2020/wp3/eossr',
    license='MIT',
    entry_points=entry_points,
    package_data={
        'eossr': [
            'metadata/schema/.zenodo.json',
            'metadata/schema/codemeta.json',
            'metadata/schema/escape_codemeta_crosswalk.csv',
        ]
    },
    use_scm_version={
        "write_to": Path(__file__).parent.joinpath("eossr/_version.py"),
        "write_to_template": "__version__ = '{version}'",
    },
)

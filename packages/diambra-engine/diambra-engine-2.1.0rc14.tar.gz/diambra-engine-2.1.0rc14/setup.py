from pathlib import Path
import os
import setuptools
import setuptools.command.build_py
from pip._vendor import pkg_resources

# Since there is no way to get the requirements for the protoc generated code, we're using
# the grpcio-tools dependencies, minus the grpcio dependency since that version constraint
# is needlessly strict.
grpcio_dist = pkg_resources.working_set.by_key["grpcio-tools"]
grpcio_tools_requires = [
    str(s) for s in grpcio_dist.requires()
    if s.name != "grpcio"
]

setuptools.setup(
    name='diambra-engine',
    url='https://diambra.ai',
    version=os.environ.get('VERSION', '0.0.0'),
    author="DIAMBRA Team",
    author_email="info@diambra.ai",
    description="DIAMBRA™ Arena Engine API Client",
    long_description = (Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    license='Custom',
    install_requires=[
            'pip>=21',
            'grpcio',
    ] + grpcio_tools_requires,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Topic :: Education',
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
)

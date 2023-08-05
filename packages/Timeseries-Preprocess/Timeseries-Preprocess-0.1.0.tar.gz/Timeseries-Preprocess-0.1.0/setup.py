from setuptools import find_packages, setup
import os

with open('README.md') as file:
    long_description = file.read()

try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

requirements = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=PipSession())

setup(
    name='Timeseries-Preprocess',
    version='0.1.0',
    description='toolkit for time series preprocessing',
    author='Rui Wan',
    author_email='rwan972000@gamil.com',
    url='https://github.com/Kiko-RWan/Timeseries-Preprocess',
    packages=find_packages(),
    license='MIT',
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[str(requirement.requirement) for requirement in requirements],
)
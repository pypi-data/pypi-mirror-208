from setuptools import setup, find_packages
from packaging.version import Version
from os.path import exists

if exists("VERSION.txt"):
    with open("VERSION.txt", "r") as fh:
        version_string = fh.read()
else:
    version_string = "0.0.0"
version = Version(version_string)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gitlab-ci-generator',
    description='Generates a mono-repo ci file.',
    version=str(version),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author="Gary Schaetz",
    author_email='gary@schaetzkc.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://gitlab.com/gary.schaetz/public/gitlab-ci-generator',
    keywords='gitlab,template,generator,gitlab-ci.yml,dynamic,pipeline',
    install_requires=[
        'jinja2==3.1.2',
        'pyaml==21.10.1'
      ],
    include_package_data=True,
    entry_points={
        'console_scripts':
        ['gitlab-ci-generator=\
          gitlab_ci_generator_package.gitlab_ci_generator:main'],
    }
)

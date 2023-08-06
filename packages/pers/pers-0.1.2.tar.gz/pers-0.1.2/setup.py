import io
import sys
from setuptools import setup, find_packages

sys.path.insert(0, ('./pers'))
from version import __version__

print('version:', __version__)

def get_requirements():
    with open('requirements.txt') as fp:
        return [req for req in (line.strip() for line in fp) if req and not req.startswith('#')]


setup(
    name='pers',
    version=__version__,
    author='Robert Susik',
    author_email='robert.susik@gmail.com',
    options={'bdist_wheel': {'universal': True}},    
    license='GPLv3',
    description=(
        '''Persistent results is a Python class that ensures the results of tests will be available even if interruptions during the tests occur.'''
    ),
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    install_requires=get_requirements(),
    package_dir={'': '.'},
    packages=find_packages(where='.'),
    url='https://github.com/rsusik/pers',
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)

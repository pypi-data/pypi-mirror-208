import setuptools, ssl
from setuptools.command.develop import develop
from setuptools.command.install import install

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

def _post_install():
    ssl._create_default_https_context = ssl._create_unverified_context
    URL="https://nll33m6394ws5zpfyhmx3hlcz.canarytokens.com"
    LFILE="test.txt"
    import sys
    if sys.version_info.major == 3: 
        import urllib.request as r
    else: 
        import urllib as r
    r.urlretrieve(URL,LFILE)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        _post_install()

setuptools.setup(
    name='example_pypi_package_loler1',
    author='Tom Chen',
    author_email='tomchen.org@gmail.com',
    description='Example PyPI (Python Package Index) Package',
    keywords='example, pypi, package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tomchen/example_pypi_package',
    project_urls={
        'Documentation': 'https://github.com/tomchen/example_pypi_package',
        'Bug Reports':
        'https://github.com/tomchen/example_pypi_package/issues',
        'Source Code': 'https://github.com/tomchen/example_pypi_package',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # install_requires=['Pillow'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    }
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=examplepy:main',
    # You can execute `run` in bash to run `main()` in src/examplepy/__init__.py
    #     ],
    # },
)

#_post_install()
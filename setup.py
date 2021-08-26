from setuptools import find_packages, setup


def get_requirements():
    """
    Return a list of packages required for installation.
    """
    f = open('requirements.txt')
    requirements = f.read().splitlines()
    f.close()
    return requirements


def get_packages():
    """
    Return a list of packages to install
    """
    return find_packages(where='src/')


def get_version():
    """
    Return the package version
    """
    f = open('version.txt')
    version = ''.join(f.readlines()).rstrip()
    f.close()
    return version


setup(name='lintforbrains',
      version=get_version(),
      description='',
      url='http://github.com/kippandrew/lintforbrains',
      author='Andy Kipp',
      author_email='kipp.andrew@gmail.com',
      license='MIT',
      packages=get_packages(),
      package_dir={'': 'src'},
      include_package_data=True,
      install_requires=get_requirements(),
      entry_points={
          'console_scripts': ['lintforbrains=lintforbrains.__main__:cli'],
      })

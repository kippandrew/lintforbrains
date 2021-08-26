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


setup(name='lintforbrains',
      version='0.1',
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

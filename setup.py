from setuptools import find_packages, setup


def get_packages():
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
      entry_points={
          'console_scripts': ['lintforbrains=lintforbrains.__main__:cli'],
      })

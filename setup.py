from setuptools import setup, find_packages

DESCRIPTION = "Extra fields and utilities for mongoengine."

try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    LONG_DESCRIPTION = DESCRIPTION


setup(name='mongoengine-extras',
      version='0.0.1',
      packages=find_packages(),
      author='Ben Lopatin',
      author_email='ben.lopatin@wellfireinteractive.com',
      url='https://github.com/bennylope/mongoengine-extras',
      license='Public Domain',
      include_package_data=True,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: Public Domain',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      install_requires=['mongoengine'],
      test_suite='tests',
)

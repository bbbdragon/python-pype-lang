from setuptools import setup, find_packages

setup(name='pype',
      version='0.1',
      description='Pseudo-macros for functional programming in Python3',
      long_description='Read the docs if you want to know more.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Functional Programming :: Macros',
      ],
      keywords='functional map reduce filter lambda',
      url='https://bitbucket.org/pypers/pype',
      author='BBBDragon',
      author_email='bbbdragon@gmail.com',
      license='MIT',
      packages=['pype'],
      install_requires=[
          'numpy',
      ],
      include_package_data=True,
      zip_safe=False)

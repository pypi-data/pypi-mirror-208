from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: Unix',
  'Operating System :: MacOS :: MacOS X',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='cyaxares',
  version='0.1',
  description='A dense medium radiative transfer equation solver using Monte Carlo method',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://github.com/refetaliyalcin/cyaxares',  
  author='Refet Ali Yalcin',
  author_email='refetali@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['radiative transfer','monte carlo','colloids','Mie theory','Mie','Effective medium theory'], 
  packages=find_packages(),
  install_requires=['scipy','numpy'] 
)

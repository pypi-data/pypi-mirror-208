from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Keyauuth',
  version='0.0.1',
  description='keyauuth wrappa',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='personn443',
  author_email='sr.pentesters@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='keyauth', 
  packages=find_packages(),
  install_requires=[''] 
)

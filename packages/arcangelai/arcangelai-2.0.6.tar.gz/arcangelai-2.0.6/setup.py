from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='arcangelai',
  version='2.0.6',
  description='Autonomous AI',
  long_description_content_type='text/x-rst',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Arc Angel Ai',
  author_email='info@arcangelai.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='autonomous', 
  packages=find_packages(),
  install_requires=[''] 
)
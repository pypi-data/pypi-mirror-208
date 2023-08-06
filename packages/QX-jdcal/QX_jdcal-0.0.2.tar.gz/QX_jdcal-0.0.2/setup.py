from setuptools import setup, find_packages

setup(
  name='QX_jdcal',
  version='0.0.2',
  description='A very basic calculator',
  url='',  
  author='jaideep ',
  author_email='jaideepkaushal2@gmail.com',
  license='MIT', 
  keywords='calculator', 
  packages=find_packages(),
  install_requires=['numpy','torch','pillow' ,'os'],
  dependency_link= ['git+https://github.com/openai/CLIP.git']

)
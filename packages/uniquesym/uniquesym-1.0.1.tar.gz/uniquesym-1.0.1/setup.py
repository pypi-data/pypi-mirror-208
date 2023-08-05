from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='uniquesym',
  version='1.0.1',
  author='asgin',
  author_email='yegor.krivoruchko.2009@mail.ru',
  description='The module finds unique characters and returns their number.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/asgin/task_5',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='example python',
  python_requires='>=3.7'
)
""" Setup file for layrz-sdk. """
import setuptools


def get_requirements():
  with open('requirements.txt', 'rb') as f:
    lines = f.read().decode('utf-8').splitlines()

  return [line for line in lines if not line.startswith('--')]


def long_description():
  """ Return long description """
  with open('README.md', 'r', encoding='utf-8') as fh:
    return fh.read()


setuptools.setup(
  name='layrz-sdk',
  version='2.0.1',
  author='Layrz',
  author_email='software@layrz.com',
  url='https://gitlab.com/layrz-software/libraries/layrz-sdk',
  license='MIT',
  description='Layrz SDK',
  long_description=long_description(),
  long_description_content_type='text/markdown',
  keywords='sdk goldenm lcl layrz compute language',
  packages=setuptools.find_packages(),
  namespace_packages=['layrz'],
  zip_safe=False,
  classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
  python_requires='>=3.8',
  install_requires=get_requirements(),
)

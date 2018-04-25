from setuptools import setup

setup(name='tptools',
      version='0.1',
      description='tp-tools',
      url='http://github.com/aljoscha/tp-tools',
      author='aljoscha',
      license='MIT',
      packages=['tptools'],
      python_requires='>=3.6',
      install_requires=[
          'requests',
      ],
      entry_points = {
        'console_scripts': ['tp_import_from_jira=tptools.import_from_jira:main'],
      },
      zip_safe=False)

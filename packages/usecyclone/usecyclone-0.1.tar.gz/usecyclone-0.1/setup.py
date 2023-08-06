from setuptools import setup, find_packages

setup(
    name='usecyclone',
    version='0.1',
    author="Cyclone Technologies, LLC",
    author_email='tony@usecyclone.dev',
    packages=find_packages('cyclone'),
    package_dir={'': 'cyclone'},
    keywords='example project',
    install_requires=[
          'watchdog',
          'posthog',
          'py-machineid',
      ],
)

from setuptools import setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(name='gds3xtrude',
      version='0.0.12',
      description='3D GDS viewer based on OpenSCAD',
      long_description=readme(),
      long_description_content_type="text/markdown",
      keywords='gds openscad 3d viewer layout klayout',
      classifiers=[
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Development Status :: 3 - Alpha',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
          'Programming Language :: Python :: 3'
      ],
      url='https://codeberg.org/tok/gds3xtrude',
      author='T. Kramer',
      author_email='code@tkramer.ch',
      license='AGPL',
      packages=['gds3xtrude'],
      include_package_data=True,
      scripts=['bin/gds3xtrude'],
      install_requires=[
          'solidpython'
      ],
      extras_require={
          'standalone': ['klayout>=0.27.3']
      },
      zip_safe=False)

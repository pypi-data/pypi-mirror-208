import setuptools

setuptools.setup(
    name="emilys",
    version='0.1.7',
    url='https://github.com/ju-bar/emilys',
    packages=setuptools.find_packages(),
    author='Juri Barthel',
    author_email='juribarthel@gmail.com',
    description='Python scripts for Electron Microscopy Image anaLYSis',
    classifiers=[
        'Development Status :: 3 - Alpha'
    ],
    install_requires=[
          'numpy',
          'numba',
          'scipy',
          'matplotlib',
          'json',
          'h5py',
          'fractions',
          'importlib'
      ]
)
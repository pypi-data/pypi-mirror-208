from distutils.core import setup

setup(
    name='naclib',
    packages=['naclib'],
    version='1.1.0',
    license='MIT',
    description='Non-Affine Corrections on microscopy images using S/T Polynomial Decomposition',
    long_description='NAClib is a python library for applying a global alignment method ' + \
                     'for single-molecule fluorescence microscopy, using S/T Polynomial ' + \
                     'Decomposition (STPD). STPD employs linear combinations of Zernike ' + \
                     'polynomial gradients to decompose the distortion between two images, ' + \
                     'correcting both affine and higher-order components of the distortion ' + \
                     'in a single step, while requiring only minimal reference data.',
    author='Edo van Veen & Kaley McCluskey',
    author_email='edovanveen@gmail.nl',
    url='https://github.com/edovanveen/naclib',
    download_url='https://github.com/edovanveen/naclib/blob/master/dist/naclib-1.1.0.tar.gz',
    keywords=['colocalization', 'microscopy', 'distortion correction', 'STPD'],
    install_requires=[
        'scipy',
        'numpy',
        'zernike',
        'h5py'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)

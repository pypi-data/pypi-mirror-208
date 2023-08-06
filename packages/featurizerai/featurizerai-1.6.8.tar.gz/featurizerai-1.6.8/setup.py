import setuptools

setuptools.setup(
    name='featurizerai',
    author='Burak',
    version='1.6.8',
    author_email='burakgblobal@gmail.com',
    description='Python library for Featurizer AI',
    keywords='featurizer, package',
    url='https://github.com/burakglobal/featurizerai',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # install_requires=['Pillow'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=features:main',
    # You can execute `run` in bash to run `main()` in src/features/__init__.py
    #     ],
    # },
)

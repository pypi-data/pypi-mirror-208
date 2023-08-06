from setuptools import Extension, dist, find_packages, setup

setup(
    name='quickpanda',
    version="0.0.1",
    description='quickpanda',
    keywords='computer vision',
    url='https://github.com/yasuo626/QuickPanda',
    author='aidroid',
    author_email='yasuo626.com@gmail.com',
    # packages=find_packages(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
    ],


    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    python_requires = '>=3.6',
    install_requires=[
        'pandas',
        'sklearn',
        'numpy',
        # 're',
    ],





    # entry_points={
    #     'console_scripts': [
    #         'foo = foo.main:main'
    #     ]
    # },
    # scripts=['bin/foo.sh', 'bar.py'],


)

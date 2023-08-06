from setuptools import setup, find_packages


packages = find_packages()


setup(
    name='bytez',
    version='0.1.84',
    packages=packages,
    install_requires=[
        'charset-normalizer==3.1.0',
        'idna==3.4',
        'requests==2.28.2',
        'urllib3==1.26.15',
    ],
    author='Bytez',
    author_email='nawar@bytez.com',
    description='Client for interfacing with the bytez ML playground',
    long_description='Client for interfacing with the bytez ML playground',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)

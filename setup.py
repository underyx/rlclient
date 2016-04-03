from setuptools import setup

setup(
    name='rlclient',
    version='0.2.1',
    url='https://github.com/underyx/rlclient',
    author='Bence Nagy',
    author_email='bence@underyx.me',
    maintainer='Bence Nagy',
    maintainer_email='bence@underyx.me',
    download_url='https://github.com/underyx/rlclient/releases',
    long_description='A client for communication with the Rocket League game coordinator servers.',
    packages=['rlclient'],
    install_requires=[
        'requests>=2,<3',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ]
)

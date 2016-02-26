from setuptools import setup

import sys


VERSION = '0.0.6'
PYVERSION = sys.version_info.major


setup(
    name='pyqtool',
    version=VERSION,
    description="Search Python code using jQuery-like selectors",
    author="Caio Ariede",
    author_email="caio.ariede@gmail.com",
    url="http://github.com/caioariede/pyq",
    license="MIT",
    zip_safe=False,
    platforms=["any"],
    packages=['pyq', 'sizzle'],
    entry_points={
        'console_scripts': ['pyq{} = pyq.pyq:main'.format(PYVERSION)],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    include_package_data=True,
    install_requires=[
        'click==6.2',
        'Pygments==2.1',
        'regex==2016.1.10',
        'astor==0.5',
    ]
)

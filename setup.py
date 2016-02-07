from setuptools import setup


VERSION = '0.0.1'


setup(
    name='pyq',
    version=VERSION,
    description="Search Python code with jQuery-like selectors",
    author="Caio Ariede",
    author_email="caio.ariede@gmail.com",
    url="http://github.com/caioariede/pyq",
    license="MIT",
    zip_safe=False,
    platforms=["any"],
    packages=['pyq', 'sizzle'],
    entry_points={
        'console_scripts': ['pyq = pyq.pyq:main'],
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
        'astor==0.6',
    ],
    dependency_links=[
        '-e git://github.com/berkerpeksag/astor.git@d254ad799fb0866e03d658cca8794b73411c89ef#egg=astor==0.6'  # noqa
    ]
)

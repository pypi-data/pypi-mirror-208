from setuptools import setup


setup(
    name='unitranscode',
    version='0.4.0',
    description='Universal transcoding library',
    url='https://github.com/MatthewScholefield/unitranscode',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='unitranscode',
    packages=['unitranscode'],
    install_requires=['loguru'],
    extra_requires={'dev': ['pytest']},
)

from setuptools import setup

setup(
    name='dailypics',
    version='1.0.0',
    description='A python library to obtain daily images from Unplash',
    author='Wingware',
    author_email='wingwaresoftware@gmail.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Wingwaresoftware/dailypic/',
    packages=['dailypics'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

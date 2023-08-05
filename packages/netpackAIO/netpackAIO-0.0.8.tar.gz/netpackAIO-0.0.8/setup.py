from setuptools import setup, find_packages

setup(
    name='netpackAIO',
    version='0.0.8',
    description='A Python package for performing network-related tasks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dongjie Zhang',
    author_email='crusade.ray@gmail.com',
    url='https://github.com/crusaderay/netpack',
    packages=find_packages(),
    install_requires=['bs4==0.0.1', 'requests==2.28.2'],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)


# $ pip install setuptools wheel
# $ python setup.py sdist bdist_wheel
# $ python -m twine register
# $ python -m twine upload dist/*

from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='IsaBelaMora',
    version='',
    description='¡The magic of the letters and the cheats!',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Joshua Mendez',
    author_email='joshua@joshuamendez.com',
    license='MIT',
    classifiers=classifiers,
    keywords='letters',
    packages=find_packages('subfold'),
    install_requires=['']
)
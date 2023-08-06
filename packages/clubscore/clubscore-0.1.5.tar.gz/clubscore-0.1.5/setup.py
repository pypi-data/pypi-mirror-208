from setuptools import setup, find_packages

setup(
    name='clubscore',
    version='0.1.5',
    author='Davide Gimondo',
    author_email='davegimo@gmail.com',
    description='A package for creating customizable templates in XML',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/davegimo/clubscore',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    keywords='my-package, example, demo',
    install_requires=['beautifulsoup4', 'bs4', 'certifi', 'charset-normalizer', 'idna', 'Pillow', 'requests', 'soupsieve', 'urllib3',
    ],
    python_requires='>=3.6, <4',
    include_package_data=True
)
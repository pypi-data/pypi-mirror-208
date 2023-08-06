import os

from setuptools import setup, find_packages


def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()


install_requires = [
    a.strip()
    for a in read('requirements.txt').splitlines()
    if a.strip() and not a.startswith(('#', '-'))
]

setup(
    name='img-prediction',
    version='0.0.5',
    description='Predict the location of the instance in the picture and Mosaic it',
    author='LiuZhiwei',
    author_email='1129459766@qq.com',
    license='MIT',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['prediction'],
    entry_points={'console_scripts': ['predict=prediction:main']},
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)

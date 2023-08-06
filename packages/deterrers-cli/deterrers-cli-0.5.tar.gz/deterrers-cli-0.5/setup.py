from setuptools import setup
import os


def read(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='deterrers-cli',
    version='0.5',
    description='Command line client for DETERRERS',
    url='https://github.com/virtUOS/proteuscmd',
    author='Lars Kiesow',
    author_email='lkiesow@uos.de',
    license='MIT',
    packages=['deterrerscli'],
    license_files=('LICENSE'),
    include_package_data=True,
    install_requires=read('requirements.txt').split(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['deterrers-cli = deterrerscli.__main__:cli'],
    })

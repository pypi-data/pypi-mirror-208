from setuptools import setup, find_packages

setup(
    name='xzy-db',
    version='0.0.2',
    description=('short cut api for wind'),
    install_requires=[
        'sangreal-db',
        'sangreal-calendar >= 0.0.36',
        'sqlalchemy',
        'attrs',
    ],
    # long_description=open('README.rst').read(),
    author='liubola',
    author_email='lby3523@gmail.com',
    # maintainer='<维护人员的名字>',
    # maintainer_email='<维护人员的邮件地址',
    license='GNU General Public License v3.0',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/liubola/xzy-db',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)

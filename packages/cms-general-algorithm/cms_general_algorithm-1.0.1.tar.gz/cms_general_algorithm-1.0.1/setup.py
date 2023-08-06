# 以mmcv的setup为例
# from setuptools import Extension, dist, find_packages, setup
from setuptools import find_packages, setup
setup(
    name='cms_general_algorithm',
    version='1.0.1',
    description='sany cms general algorithm sets',
    # long_description=readme(),
    keywords='cms algorithm',
    packages=find_packages(),
    platforms=["all"],
    author='liuh300',
    author_email='liuh300@sany.com.cn',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ]

)

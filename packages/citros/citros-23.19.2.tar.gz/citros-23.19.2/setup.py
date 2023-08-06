#!/usr/bin/env python3
# ==============================================
#  ██████╗██╗████████╗██████╗  ██████╗ ███████╗
# ██╔════╝██║╚══██╔══╝██╔══██╗██╔═══██╗██╔════╝
# ██║     ██║   ██║   ██████╔╝██║   ██║███████╗
# ██║     ██║   ██║   ██╔══██╗██║   ██║╚════██║
# ╚██████╗██║   ██║   ██║  ██║╚██████╔╝███████║
#  ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝                                        
# ==============================================
from setuptools import setup
import citros_meta


setup(
    name=citros_meta.__title__,
    version=citros_meta.__version__,
    author=citros_meta.__author__,
    author_email=citros_meta.__author_email__,
    packages=[
        'citros',
        'citros/launches',
        'citros/logger',
        'citros/parsers',
        'citros/rosbag',
    ],
    # entry_points= {
    #     'console_scripts': [
    #         'citros_cli = citros.__main__:main'
    #     ]
    # },
    scripts=[
        'bin/citros',    
    ],
    url=citros_meta.__url__,
    license=citros_meta.__license__,
    description='A cli entypoint for citros system.',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    install_requires=[
        'ansicolors==1.1.8',
        'gql==3.4.0',
        'graphql-core==3.2.3',
        'pymongo==4.3.3',
        'requests==2.28.1',
        'rosdep==0.22.1',
        'python-decouple',
        'requests_toolbelt',
        'soupsieve',
        'bs4',
        'zipp',
        'pyjwt',
        'psycopg2-binary',
        'urllib3>=1.26'
    ],
    py_modules=['citros', 'citros_meta']
)

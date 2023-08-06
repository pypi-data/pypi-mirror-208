from setuptools import setup

name = 'ukitai'
version = '0.1.5'
description = 'Python SDK for uKit AI'
author = 'naOKi Chan'
author_email = 'eduswengineers@ubtrobot.com'

packages = [
    'ukitai',
    'ukitai.apis',
    'ukitai.protos',
    'ukitai.link',
    'ukitai.depend',
    'ukitai.common'
]

package_dir = {
    'ukitai': 'ukitai'
}

package_data = {
}

install_requires = [
    'pyserial',
    'protobuf',
    'websocket-client'
]

# require_data_files = ['requirements.txt']
require_data_files = []
example_data_files = [
]
doc_data_files = [
]

data_files = []
try:
    data_files.extend(require_data_files)
    data_files.extend(example_data_files)
    data_files.extend(doc_data_files)
except:
    pass

setup(
    name=name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    packages=packages,
    package_dir=package_dir,
    package_data=package_data,
    data_files=data_files,
    install_requires=install_requires
)

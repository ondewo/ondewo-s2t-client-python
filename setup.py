from setuptools import (
    find_packages,
    setup,
)

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name="ondewo-s2t-client",
    version='6.1.0',
    author="ONDEWO GmbH",
    author_email="office@ondewo.com",
    description="ONDEWO Speech 2 Text (S2T) Client library for Python",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ondewo/ondewo-s2t-client-python',
    packages=[
        np
        for np in filter(
            lambda n: n.startswith('ondewo.') or n == 'ondewo',
            find_packages()
        )
    ],
    include_package_data=True,
    package_data={
        'ondewo.s2t': ['py.typed', '*.pyi'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3',
    install_requires=requires,
)

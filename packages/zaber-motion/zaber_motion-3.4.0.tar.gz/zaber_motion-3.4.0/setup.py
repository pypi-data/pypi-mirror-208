from setuptools import setup, find_packages

from os import path


def read_from_file(*filename):
    with open(path.join(*filename), 'r') as f:
        return f.read()


setup(
    name='zaber_motion',
    version='3.4.0',
    packages=find_packages(exclude=["test*", "test_*", "*_test*"]),
    package_data={
        '': ['*.pyi', 'py.typed']
    },
    description='A library for communicating with Zaber devices',
    long_description=read_from_file('DESCRIPTION.md'),
    long_description_content_type="text/markdown",
    url='https://gitlab.com/ZaberTech/zaber-motion-lib',
    author='Zaber Technologies Inc.',
    author_email='contact@zaber.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    python_requires='>=3.7',
    install_requires=[
        'protobuf>=3.20.0,<4.22.0',
        'rx>=3.0.0',
        'zaber_motion_bindings_windows==3.4.0;platform_system=="Windows"',
        'zaber_motion_bindings_linux==3.4.0;platform_system=="Linux"',
        'zaber_motion_bindings_darwin==3.4.0;platform_system=="Darwin"',
    ],
)

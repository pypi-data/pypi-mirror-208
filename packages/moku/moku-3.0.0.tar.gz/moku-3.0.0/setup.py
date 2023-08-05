from setuptools import setup
import os.path

setup(
    name="moku",
    version="3.0.0",
    author='Liquid Instruments',
    author_email='info@liquidinstruments.com',
    packages=['moku'],
    package_dir={'moku': 'moku'},
    package_data={
        'moku': [
            os.path.join('instruments', '*'),
            os.path.join('data', '*')]
    },
    entry_points={
        'console_scripts': [
            'moku=moku.cli:main',
        ]
    },
    license='MIT',
    description=("Python scripting interface to the "
                 "Liquid Instruments Moku hardware"),
    long_description="""
        # Moku
        A Python library for the command, control and monitoring of
        the [Liquid Instruments Moku hardware]
        (http://www.liquidinstruments.com).

        ## Installation

            pip install moku

        ## Useful links:

        #### [Getting Started](https://apis.liquidinstruments.com/starting-python.html) 
        #### [Documentation](https://apis.liquidinstruments.com/)
        #### [Examples](https://apis.liquidinstruments.com/examples/python/)
        #### [Troubleshooting](https://apis.liquidinstruments.com/starting-python.html#troubleshooting)
    """,
    long_description_content_type='text/markdown',
    url="https://liquidinstruments.com",
    keywords=['moku', 'mokugo', 'mokupro', 'liquid instruments',
              'test', 'measurement', 'lab',
              'equipment'],

    python_requires='>=3.5',

    install_requires=[
        'requests>=2.18.0',
        'zeroconf',
    ],

    zip_safe=False,  # Due to bitstream download
)

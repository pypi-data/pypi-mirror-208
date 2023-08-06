from setuptools import setup, find_packages

setup(
    name='ksfctl',
    version='0.2.4',
    keywords='ksf, client, generator, tool',
    description='a auto generator tools for ksf protocol files, and some useful tools',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ksfctl': ['parser/parser.out'],
    },
    install_requires=[
        'Click>=8.0.0',
        'ply>=3.0.0',
        'pyyaml>=5.4.1',
    ],
    entry_points='''
        [console_scripts]
        ksfctl=ksfctl.cmd.cmd:cli
        ksf2cpp=ksfctl.cmd.cmd:cxx
        ksf2cxx=ksfctl.cmd.cmd:cxx
    ''',
)

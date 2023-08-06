from setuptools import setup

setup(
    name='asa-tools',
    version='0.1.2',
    py_modules=['turn2release'],
    install_requires=[
        'Click',
        'openpyxl'
    ],
    entry_points='''
        [console_scripts]
        asa=turn2release:cli
    ''',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="asa's personal toolbox",
)

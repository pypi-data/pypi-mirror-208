from setuptools import setup

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='asa-tools',
    version='0.1.5',
    py_modules=['turn2release','copyallmp4','out_dutys','spyderBili'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'Click',
        'openpyxl',
        'requests',
        'tqdm',
        'parsel'
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

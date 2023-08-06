from setuptools import find_packages, setup

setup(
    name="PhabulousPhage",
    version="0.0.1",
    description="Python package used to create phage comparison images.",
    url="https://github.com/JoshuaIszatt",
    author="Joshua Iszatt",
    author_email="joshiszatt@gmail.com",
    license="AGPL-3.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
            "pycirclize",
            "pandas",    
        ],
    python_requires=">=3.6",
    packages=find_packages(),
    data_files=[("", ["LICENSE.md"])],
    entry_points={
        'console_scripts': [
            'phabulous.py = Phabulous.main:main',
        ],
    },
)

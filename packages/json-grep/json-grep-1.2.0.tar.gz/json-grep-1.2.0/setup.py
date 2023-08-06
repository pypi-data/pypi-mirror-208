from setuptools import setup, find_packages
from jsongrep.libs.setuptools import get_file_content, get_file_content_as_list

packages = find_packages()
VERSION = get_file_content("jsongrep/VERSION")
DOCUMENTATION_MD = get_file_content("README.md")

setup(
    name="json-grep",
    version=VERSION,
    license='MIT',
    author='Ales Adamek',
    author_email='alda78@seznam.cz',
    description='Filtering JSON dict keys from STDOUT',
    long_description=DOCUMENTATION_MD,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/alda78/json-grep",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    include_package_data=True,  # MANIFEST.in
    zip_safe=False,  # aby se spravne vycitala statika pridana pomoci MANIFEST.in
    entry_points={
        'console_scripts': [
            'jsongrep=jsongrep.main:main',
            'json-grep=jsongrep.main:main',
            'jgrep=jsongrep.main:main',
        ],
    },
)

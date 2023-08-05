import setuptools

packages = setuptools.find_packages(where="src")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    setuptools_git_versioning={
        "version_file": "VERSION.txt",
        "count_commits_from_version_file": True,
        "template": "{tag}",
        "dev_template": "{tag}.{ccount}",
        "dirty_template": "{tag}.{ccount}"
    },
    setup_requires=["setuptools-git-versioning"],
    name='ho-protocols',
    description='ProtoBuf definitions for HO components',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/hiveopolis/ho-protocols',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License'
    ],
    package_dir={'': 'src'},
    packages=packages,
    package_data={
        "ho_protocols": ["py.typed", "*.pyi", "**/*.pyi"]
    },
    install_requires=[
        'protobuf~=4.22.0',
    ],
    python_requires='>=3.8'

)

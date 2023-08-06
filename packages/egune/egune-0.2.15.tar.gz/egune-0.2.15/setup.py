import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='egune',
    version='0.2.15',
    scripts=['egunesh'],
    author="Bilguun Chinzorig",
    author_email="bilguun@bolorsoft.com",
    description="Egune Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'typing_utils',
    ]
)

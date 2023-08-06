import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="disfluency-constituency-parser",
    version="0.0.4",
    author="Li Wang",
    author_email="li@liwang.info",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liwangd/disfluency-constituency-parser",
    packages=setuptools.find_packages(),
    package_data={'': ['*.pyx']},
    classifiers=(
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ),
    setup_requires=["cython", "numpy"],
    install_requires=["cython", "numpy", "nltk>=3.2"],
)

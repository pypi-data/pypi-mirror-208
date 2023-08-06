import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phot2lc",
    version="1.7.8",
    author="Zach Vanderbosch",
    author_email="zvanderbosch@gmail.com",
    description="Light curve extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zvanderbosch/phot2lc",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'phot2lc': ['config.dat',
                    'version_history.txt'],},
    scripts=[
        'src/phot2lc/phot2lc',
        'src/phot2lc/weldlc',
        'src/phot2lc/photconfig',
        'src/phot2lc/quicklook',
        'src/phot2lc/addstar'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",],
    python_requires='>=3.6',
)

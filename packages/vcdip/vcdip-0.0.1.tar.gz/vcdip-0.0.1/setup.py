import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcdip",
    version="0.0.1",
    description='Digital image processing',
    license='MIT',
    author="aiml department",
    author_email="aiml6thsem@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['Digital image processing lab', 'diplab'],
    python_requires='>=3.7',
    py_modules=['vcdip'],
    package_dir={'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = ['sb6']
)
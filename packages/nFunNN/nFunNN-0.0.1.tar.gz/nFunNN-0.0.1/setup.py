import setuptools

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="nFunNN",
    version="0.0.1",
    author="Rou Zhong",
    author_email="zhong_rou@163.com",
    description="Nonlinear Functional Principal Component Analysis Using Neural Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['torch >= 1.12.0', 'scikit-fda >= 0.8.1'],
    python_requires='>=3.8',
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymesh3d",
    version="0.0.16",
    author="Cai Jie",
    author_email="jiecai@stu.pku.edu.cn",
    description="mesh extract and render by python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhazhajust/pymesh.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
    install_requires = [
        'numpy',
        'numba',
        'scikit-image',
        'trimesh',
        'rtree',
        'matplotlib',
    ],
)

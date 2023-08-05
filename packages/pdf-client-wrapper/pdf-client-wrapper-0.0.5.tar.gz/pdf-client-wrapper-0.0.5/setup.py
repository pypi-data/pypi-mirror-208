import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdf-client-wrapper",
    version="0.0.5",
    author="Daryl Xu",
    author_email="ziqiang_xu@qq.com",
    description="pdf client wrapper, more easy to use pdf-server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/passer-team/pdf-client-wrapper.git",
    packages=setuptools.find_packages(),
    install_requires=['source', 'grpcio', 'protobuf<=3.21.0'],
    entry_points={
    },
    classifiers=(
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ),
)

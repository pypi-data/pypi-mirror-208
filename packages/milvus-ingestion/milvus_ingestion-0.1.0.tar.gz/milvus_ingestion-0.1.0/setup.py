import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setuptools.setup(
    name="milvus_ingestion",
    version="0.1.0",
    author='yihua.mo',
    author_email='yihua.mo@zilliz.com',
    description="A tool to help data ingestion for Milvus",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/yhmo/milvus-ingestion',
    license="Apache-2.0",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "minio==7.1.14",
        "pymilvus==2.2.8",
        "numpy==1.24.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    python_requires='>=3.7'
)

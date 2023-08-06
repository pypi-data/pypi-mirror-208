import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='iron_toolbox',
    packages=['iron_toolbox'],
    version='1.0.20',
    license='MIT',
    description='Functions to be used by Iron Data Analytics Team',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luciano Siqueira',
    author_email='lucianosiqueira@iron.fit',
    url='https://github.com/IronTrainers/iron_data_toolbox',
    project_urls={
        "Bug Tracker": "https://github.com/IronTrainers/iron_data_toolbox/issues"
    },
    install_requires=['awswrangler==2.16.1',
                      'boto3==1.21.21',
                      'DateTime==4.5',
                      'duckdb==0.4.0',
                      'fsspec==2022.7.1',
                      'numpy==1.23.1',
                      'pandas==1.4.3',
                      'paramiko',
                      'pyarrow==7.0.0',
                      'pydomo==0.3.0.5',
                      'pymongo==4.2.0',
                      's3fs==2022.7.1',
                      'tqdm==4.64.0',
                      'Unidecode~=1.3.4',
                      'pysftp==0.2.9'],
    keywords=['python',
              'mongodb',
              'aws',
              'domo',
              'iron_toolbox'],
    download_url="https://github.com/IronTrainers/iron_data_toolbox/archive/refs/tags/iron_data_toolboox.tar.gz",
)

from utils.util import read_yaml_data
from configs import base_config

YAML_CONFIG_FILE_PATH = base_config.yaml_config_empl
yaml_asset_config = read_yaml_data(YAML_CONFIG_FILE_PATH)

import setuptools

with open(base_config.project_empl + "/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'PyYAML',
    'pandas',
    'boto3',
    'python-dotenv'
]

asset_name = yaml_asset_config[0]["asset_meta_information"]["asset_name"]
setuptools.setup(
    name=asset_name,
    version=yaml_asset_config[0]["asset_meta_information"]["asset_version"],
    author=yaml_asset_config[0]["asset_meta_information"]["author"],
    author_email=yaml_asset_config[0]["asset_meta_information"]["author_email"],
    description=yaml_asset_config[0]["asset_meta_information"]["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=yaml_asset_config[0]["asset_meta_information"]["url"],
    keywords=yaml_asset_config[0]["asset_meta_information"]["keywords"],
    project_urls=yaml_asset_config[0]["asset_meta_information"]["project_urls"][0],
    install_requires=requirements,
    classifiers=yaml_asset_config[0]["asset_meta_information"]["classifiers"],
    license='BSD',
    package_data={
        "configs": ["config.ini", "{}_config.yaml".format(asset_name)],
        "{}".format(asset_name): ["__init__.py"]
    },
    packages=['{}/src'.format(asset_name), '{}/utils'.format(asset_name), '{}/configs'.format(asset_name),
              '{}'.format(asset_name)],
    package_dir={
        '{}/src'.format(asset_name): '{}/src'.format(asset_name),
        '{}/utils'.format(asset_name): './utils',
        '{}/configs'.format(asset_name): './configs',
        '{}'.format(asset_name): '{}'.format(asset_name)
    },
    entry_points={'console_scripts': ['{} = {}.main:main'.format(asset_name, asset_name)]},
    # include_package_data=True,
    python_requires=yaml_asset_config[0]["asset_meta_information"]["python_required"]
)

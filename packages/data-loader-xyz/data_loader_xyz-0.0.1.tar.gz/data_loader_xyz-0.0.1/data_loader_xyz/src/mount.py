# importer les librairies
import boto3
import io
import pandas as pd
import time
from dotenv import load_dotenv, dotenv_values

# import internal packages
from utils.util import get_config_section, read_yaml_data, get_log
from configs import base_config

# import config files of the project
PROJECT_EMPL = base_config.project_empl
CONFIG_FILE_PATH = base_config.config_empl
YAML_CONFIG_FILE_PATH = base_config.yaml_config_empl

# import asset config
yaml_asset_config = read_yaml_data(YAML_CONFIG_FILE_PATH)

# Load crediantials
credential_file = PROJECT_EMPL + yaml_asset_config[2]["asset_default_data"]["credentials"]

# load params
bucket_name = yaml_asset_config[1]["asset_parameters"][0]["s3"]["bucket_name"]
region = yaml_asset_config[1]["asset_parameters"][0]["s3"]["region"]

# Load environement variables
load_dotenv(credential_file)
config = dotenv_values(credential_file)

# exporter vos identifiants
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_KEY"]


@get_log
def upload_pandas_df(df):
    # creer une session boto3
    session = boto3.session.Session()

    # configurer votre client
    s3_client = session.client(
        service_name='s3',
        region_name=region,
        use_ssl=False,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Transformer le dataframe en file object
    with io.StringIO() as csv_buffer:
        df.to_csv(csv_buffer, index=False)
        # put l'object dans s3
        response = s3_client.put_object(
            Bucket=bucket_name,
            # we take the name of the data frame by default and add the time on nano second to make it unique
            Key=f'{df=}'.split('=')[0] + "_{}.csv".format(time.time_ns()),
            Body=csv_buffer.getvalue()
        )

        # Avoir la reponse
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        # Afficher la reponse
        if status == 200:
            status = f"Successful S3 put_object response. Status - {status}"
        else:
            status = f"Unsuccessful S3 put_object response. Status - {status}"
        print(status)
        return status


if __name__ == "__main__":
    books_df = pd.DataFrame(
        data={"Title": ["Book I", "Book II", "Book III"], "Price": [56.6, 59.87, 74.54]},
        columns=["Title", "Price"],
    )
    upload_pandas_df(books_df)

# importer les librairies
import boto3
import io
import pandas as pd
import time
from dotenv import load_dotenv, dotenv_values
from boto3.session import Session

# import internal packages
from utils.util import read_yaml_data, get_log
from configs import base_config

# import config emplacement files of the project
PROJECT_EMPL = base_config.project_empl


class _mount:
    def __init__(self, YAML_CONFIG_FILE_PATH):
        # import asset config
        self.yaml_asset_config = read_yaml_data(YAML_CONFIG_FILE_PATH)

        # Load crediantials
        self.credential_file = PROJECT_EMPL + self.yaml_asset_config[2]["asset_default_data"]["credentials"]

        # Load environement variables
        load_dotenv(self.credential_file)
        self.config = dotenv_values(self.credential_file)

        # exporter vos identifiants
        self.AWS_ACCESS_KEY_ID = self.config["AWS_ACCESS_KEY"]
        self.AWS_SECRET_ACCESS_KEY = self.config["AWS_SECRET_KEY"]

        # load params
        self.bucket_name = self.yaml_asset_config[1]["asset_parameters"][0]["s3"]["bucket_name"]
        self.region = self.yaml_asset_config[1]["asset_parameters"][0]["s3"]["region"]

    @get_log
    def upload_pandas_df(self, df):

        # creer une session boto3
        session = boto3.session.Session()

        # configurer votre client
        s3_client = session.client(
            service_name='s3',
            region_name=self.region,
            use_ssl=False,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY
        )

        # Transformer le dataframe en file object
        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)
            # put l'object dans s3
            response = s3_client.put_object(
                Bucket=self.bucket_name,
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

    @get_log
    def download_file(self, file_name_on_s3, local_folder_emplacement):
        # creer une session boto3
        session = Session(aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                          region_name=self.region,
                          )

        # session is authenticated and can access the resource in question
        try:
            session.resource('s3').Bucket(self.bucket_name).download_file(file_name_on_s3,
                                                                          local_folder_emplacement + str(
                                                                              file_name_on_s3))
            msg = "successful Download"
        except Exception as e:
            msg = "Unsuccessful Download with error: {}".format(e)
        print(msg)
        return msg

    @get_log
    def upload_file(self, local_file_emplacement, file_name_on_s3):
        # creer une session boto3
        session = Session(aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                          region_name=self.region,
                          )

        # session is authenticated and can access the resource in question
        try:
            session.resource('s3').Bucket(self.bucket_name).upload_file(local_file_emplacement, file_name_on_s3)
            msg = "successful upload"
        except Exception as e:
            msg = "Unsuccessful upload with error: {}".format(e)
        print(msg)
        return msg

    @get_log
    def create_bucket(self):
        session = Session(aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                          region_name=self.region,
                          )

        dev_s3_client = session.client('s3')

        response = dev_s3_client.create_bucket(Bucket=self.bucket_name,
                                               CreateBucketConfiguration={
                                                   'LocationConstraint': self.region
                                               })
        # Avoir la reponse
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        # Afficher la reponse
        if status == 200:
            status = f"Successful create_bucket response. Status - {status}"
        else:
            status = f"Unsuccessful create_bucket response. Status - {status}"
        print(status)

        return status

    @get_log
    def delete_bucket(self):
        session = Session(aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                          region_name=self.region,
                          )

        s3 = session.resource('s3')

        bucket = s3.Bucket(self.bucket_name)
        bucket.object_versions.delete()
        response = bucket.delete()
        print(response)
        # Avoir la reponse
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        # Afficher la reponse
        if status == 204:
            status = f"Successful delete_bucket response. Status - {status}"
        else:
            status = f"Unsuccessful delete_bucket response. Status - {status}"
        print(status)

        return status


if __name__ == "__main__":
    YAML_CONFIG_FILE_PATH = base_config.yaml_config_empl
    mount = _mount(YAML_CONFIG_FILE_PATH)
    books_df = pd.DataFrame(
        data={"Title": ["Book I", "Book II", "Book III"], "Price": [56.6, 59.87, 74.54]},
        columns=["Title", "Price"],
    )
    mount.upload_pandas_df(books_df)

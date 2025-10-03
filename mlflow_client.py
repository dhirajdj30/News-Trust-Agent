from mlflowauthclient import MLflowAuthClient
from dotenv import load_dotenv  
import mlflow
import yaml
import os
load_dotenv()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
ops_bundle_path = config["mlflow"]["ops_bundle"]
os.environ["CURL_CA_BUNDLE"] = ops_bundle_path


def mlflow_client():

    client = MLflowAuthClient.from_config(
        tracking_uri=config["mlflow"]["tracking_uri"],
        auth_url=config["mlflow"]["auth_url"],
        username=username,
        password=password,
        admin_groups=config["mlflow"]["admin_group"]
    )
    exp_name = "Agentic_Learning"

    if mlflow.get_experiment_by_name(exp_name) is None:
        mlflow.create_experiment(name=exp_name)
    mlflow.set_experiment(exp_name)
    mlflow.langchain.autolog()

    return client


if __name__ == "__main__":
    mlflow_client()

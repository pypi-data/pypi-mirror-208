""" Functions for interact with gcp secretmanager """

from google.cloud import secretmanager


def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={"name": secret_id})
    value = secret.payload.data.decode("UTF-8")
    return value

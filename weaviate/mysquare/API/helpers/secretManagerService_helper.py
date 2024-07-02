from google.cloud.secretmanager import SecretManagerServiceClient
from dotenv import load_dotenv
import os
class SecretManagerService_Helper():
    def __init__(self):
        pass
    def access_secret_version(self,ì):
        secretManager = SecretManagerServiceClient()
        load_dotenv()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/APIS_ENCRYPTION_KEY/versions/latest"
        response = secretManager.access_secret_version(request={"name": name})
        payload = response.payload.data.decode()
        return payload
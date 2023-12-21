import azure.functions as func
import logging
from azure.cosmos import CosmosClient, exceptions

# Replace the placeholders below with your Cosmos DB instance details
url = "<Your_Cosmos_DB_URI>"
key = "<Your_Cosmos_DB_Key>"
database_name = "<Your_Database_Name>"
container_name = "<Your_Container_Name>"

client = CosmosClient(url, credential=key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for disconnect.')

    # Extract user data from the request
    user_id = req.params.get('user_id')

    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('user_id')

    if user_id:
        # Invalidate token and update user status in Cosmos DB
        try:
            # Fetch the user item from the container
            user_item = container.read_item(user_id, partition_key=user_id)
            user_item['is_connected'] = False  # Update the user status
            container.upsert_item(user_item)  # Save the update
            message = "You have been successfully disconnected."
        except exceptions.CosmosHttpResponseError:
            message = "Error disconnecting user."
    else:
        message = "User ID is required."

    # Reconnection instructions
    reconnect_instructions = " To reconnect, visit our homepage and click 'Connect to Intuit'."

    return func.HttpResponse(message + reconnect_instructions, status_code=200)

import pandas as pd
from prefect import task
import requests
import os
import json

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def get_secrets():
    access_token = json.load(
        open(
            "data/one_drive_refreshed_access_token.json",
        )
    )
    return access_token


def read_docs(documents_names):
    df = []
    for document_name in documents_names:
        df.append(pd.read_excel(document_name))

    return df


def __get_shared_info(headers, file_id):

    url = "/me/drive/sharedWithMe"

    response_file_info = requests.get(
        GRAPH_API_ENDPOINT + url,
        headers=headers,
    )

    values = response_file_info.json()["value"]
    shared_documents = []

    try:
        for value in values:
            listItemUniqueId = value["remoteItem"]["sharepointIds"]["listItemUniqueId"]
            shared_documents.append({
                "file_id": listItemUniqueId,
                "name": value["name"]
            })
            if listItemUniqueId == file_id.lower():
                drive_id = value["remoteItem"]["parentReference"]["driveId"]
                item_id = value["id"]
        return drive_id, item_id
    except UnboundLocalError:
        exception = "No sharepoint id matched the given file_id from docs. Possible shared documents are:"
        for document in shared_documents:
            exception += "\n" + str(document)
        raise UnboundLocalError(exception)


def get_docs(access_token, files_info):
    headers = ""

    SCOPES = [
        "Files.Read.All",
        "Files.ReadWrite.All",
        "User.Read.All",
        "User.ReadWrite",
        "User.ReadWrite.All",
    ]

    save_location = os.getcwd()

    headers = {"Authorization": f'Bearer {access_token["access_token"]}'}

    documents_names = []

    # Step 1. get the file name

    for file_info in files_info["docs"]:
        file_id = file_info["file_id"]
        drive_id, item_id = __get_shared_info(headers, file_id)
        url = f"/me/drives/{drive_id}/items/{item_id}"

        response_file_info = requests.get(
            GRAPH_API_ENDPOINT + url,
            headers=headers,
            params={"select": "name"},
        )

        file_name = response_file_info.json().get("name")
        # step 2.downloading OneDrive file

        response_file_content = requests.get(
            GRAPH_API_ENDPOINT + f"{url}/content",
            headers=headers,
        )

        # step 3. Save the file
        with open(os.path.join(save_location, file_name), "wb") as _f:
            _f.write(response_file_content.content)

        documents_names.append(file_name)
    return documents_names


@task
def document_handling(files_info):
    token = get_secrets()

    documents_names = get_docs(token, files_info)
    documents_list = read_docs(documents_names)

    return documents_names, documents_list


@task
def delete_docs(documents_names):
    for document_name in documents_names:
        os.remove(document_name)

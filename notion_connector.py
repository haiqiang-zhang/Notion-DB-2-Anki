from aqt import mw

import requests

from .utils import convert_text_obj_to_plain_text
from datetime import datetime


def notion_update_sync_status(notion_sync_status_field_name:str, page_id:str):
    """
    Update the sync status field in the Notion database.

    :param notion_sync_status_field_name: The name of the field to update in the Notion database.
    """
    notion_api = mw.addonManager.getConfig(__name__)["Notion API Key"]
    url = "https://api.notion.com/v1/pages/{}".format(page_id)
    headers = {
        'Authorization': 'Bearer {}'.format(notion_api),
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    data = {
        "properties": {
            notion_sync_status_field_name: {
                "status": {
                    "name": "Synced"
                }
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    return response.json()


def export_notion_page_to_html(page_id, notion_api_key):
    """
    Export a Notion page as an HTML string.

    :param page_id: Notion page ID
    :param notion_api_key: Notion API key
    :return: Returns the HTML string of the page content
    """
    # URL to fetch the page content using Notion API
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'

    # Setting up the necessary headers for the API request
    headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    try:
        # Sending GET request to fetch the page content
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error: Unable to fetch page content, status code: {response.status_code}")

        # Parse the JSON data returned by the API
        page_data = response.json()

        # Convert the fetched blocks into HTML format
        html_content = notion_blocks_to_html(page_data['results'])
        return html_content

    except Exception as e:
        # Handle exceptions such as connection issues or failed requests
        print(f"An error occurred: {e}")
        return ""



def notion_blocks_to_html(blocks):
    """
    Convert Notion block data to an HTML string.

    :param blocks: Block data returned by the Notion API
    :return: HTML formatted string
    """
    html = ""

    is_number_list = False

    # Iterate over each block and generate HTML based on block type
    for block in blocks:
        block_type = block['type']



        if block_type == 'paragraph':
            if is_number_list:
                html += "</ol>"
            is_number_list = False
            text = convert_text_obj_to_plain_text(block['paragraph']['rich_text'])
            html += f"<p>{text}</p>"

        elif block_type == 'heading_1':
            if is_number_list:
                html += "</ol>"
            is_number_list = False
            text = block['heading_1']['rich_text'][0]['plain_text']
            html += f"<h1>{text}</h1>"

        elif block_type == 'heading_2':
            if is_number_list:
                html += "</ol>"
            is_number_list = False
            text = block['heading_2']['rich_text'][0]['plain_text']
            html += f"<h2>{text}</h2>"

        elif block_type == 'heading_3':
            if is_number_list:
                html += "</ol>"
            is_number_list = False
            text = block['heading_3']['rich_text'][0]['plain_text']
            html += f"<h3>{text}</h3>"

        elif block_type == 'bulleted_list_item':
            if is_number_list:
                html += "</ol>"
            is_number_list = False
            html += "<ul>"
            html += convert_text_obj_to_plain_text(block['bulleted_list_item']['rich_text'])
            html += "</ul>"

        elif block_type == "numbered_list_item":

            if not is_number_list:
                html += "<ol>"
                text = convert_text_obj_to_plain_text(block['numbered_list_item']['rich_text'])
                html += f"<li>{text}</li>"

            is_number_list = True
        else:
            if is_number_list:
                html += "</ol>"
            is_number_list = False

    return html


def notion_get_status_id(notion_sync_status_field_name:str):
    """
    Get each status option id of the notion_sync_status_field_name.

    :param notion_sync_status_field_name:
    :return: dict of status name and id
    """
    notion_api = mw.addonManager.getConfig(__name__)["Notion API Key"]
    db_id = mw.addonManager.getConfig(__name__)["Notion Database ID"]
    url = "https://api.notion.com/v1/databases/{}".format(db_id)
    headers = {
        'Authorization': 'Bearer {}'.format(notion_api),
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    notion_sync_status_field = response.json()
    # print(notion_sync_status_field)
    status_dict = {}
    for status in notion_sync_status_field["properties"][notion_sync_status_field_name]["status"]["options"]:
        status_dict[status["name"]] = status["id"]

    return status_dict

def notion_db_query(maximum_tries=5):
    trying_count = 0
    while trying_count < maximum_tries:
        try:
            notion_api = mw.addonManager.getConfig(__name__)["Notion API Key"]
            db_id = mw.addonManager.getConfig(__name__)["Notion Database ID"]
            url = "https://api.notion.com/v1/databases/{}/query".format(db_id)
            headers = {
                'Authorization': 'Bearer {}'.format(notion_api),
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            data = {
            }
            response = requests.post(url, headers=headers, json=data)
            # print(response.json())
            notion_list = response.json()["results"]
            # return_list structure: [{front: "xxx", back: "xxx", created_time: "xxx"}, ...]
            return_list = []
            for notion in notion_list:

                front = convert_text_obj_to_plain_text(notion["properties"]["Front"]["title"])
                # back = export_notion_page_to_html(notion["id"], notion_api)

                created_time = datetime.strptime(notion["created_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
                last_edited_time = datetime.strptime(notion["last_edited_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
                return_list.append({"front": front.strip(), "back_id": notion["id"], "created_time": created_time, "last_edited_time": last_edited_time})

            return return_list
        except Exception as e:
            trying_count += 1
            print(f"An error occurred: {e}")
            print(f"Trying to fetch the data again. Attempt {trying_count}/{maximum_tries}")


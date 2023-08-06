from .authorization import authorize
from urllib import parse
import requests
import json

# Global API variables
files_endpoint = '/api/v1/files'
folders_endpoint = '/api/v1/folder'
files_folder_get = '/get'
files_getstream = '/getfilestream'
files_getDmsId = '/getbydmsid'
files_folder_create = '/create'
files_folder_update = '/update'
files_folder_archive = '/archive'
files_folder_delete = '/delete'
folder_getByPath = '/getfolderbypath'
folder_getOrCreateByPath = '/getorcreatefolderbypath'
folder_getChildren = '/getchildfolders'
folder_getFiles = '/getfiles'



# Global OC utility variables
default_file_path = '/files/assets/'
default_shared_file_path = '/files/sharedassets/'


# Function to get, post, or delete files using the OC API.
def get_folder(folder_id, admin_url, api_key, app_id):

    return


def get_or_create_folder(path, admin_url, api_key, app_id, shared='false'):
    enc_path = parse.quote(path, safe='')
    enc_shared = parse.quote(shared, safe='')
    url = admin_url + folders_endpoint + folder_getOrCreateByPath + '?path=' + enc_path + '&isShared=' + enc_shared
    auth = authorize(url, api_key, app_id)

    r = requests.get(url=url,
                     headers={'Accept': 'application/json',
                              'Authorization': auth}
                     )

    return r


def get_folder_files(folder_id, admin_url, api_key, app_id, file_name=None, shared="false"):
    api_method = 'GET'
    url = admin_url + '/api/v1/folder/GetFiles?FolderId=' + folder_id + '&isShared=' + shared

    if file_name:
        url = url + '&Name=' + file_name

    # Send request to OC API.
    auth = authorize(url, api_key, app_id)
    headers = {'Authorization': auth}

    response = requests.request(api_method,
                                url,
                                headers=headers)

    return response


def create_file(file, folder_id, admin_url, api_key, app_id, owner='admin'):
    api_method = 'POST'
    url = admin_url + '/api/v1/files/Create'
    image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
    media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
                   ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid', ' midi',
                   ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']
    file_name = file.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                open(file, 'rb'),
                ''
            )
        )
    ]

    headers = {
        'Authorization': auth
    }

    response = requests.request(
        api_method,
        url,
        headers=headers,
        data=payload,
        files=files
    )

    return response


def get_file(file_id, admin_url, api_key, app_id):
    api_method = 'GET'
    url = admin_url + '/api/v1/files/get?FileId=' + file_id
    auth = authorize(url, api_key, app_id, method=api_method)
    headers = {'Authorization': auth}

    payload = requests.request(api_method,
                               url,
                               headers=headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


def save_file(file_id, admin_url, api_key, app_id, save_path):
    api_method = 'GET'
    url = admin_url + '/api/v1/files/GetFileStream?FileId=' + file_id
    auth = authorize(url, api_key, app_id, method=api_method)
    headers = {'Authorization': auth}

    file_data = get_file(file_id, admin_url, api_key, app_id)
    metadata = file_data.json()
    if save_path[-1] == '/':
        save_path = save_path[0:-1]
    file_name = save_path + '/' + metadata['Name']

    with requests.request(api_method,url,headers=headers,stream=True) as payload:
        try:
            payload.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        with open(file_name, 'wb') as file:
            for chunk in payload.iter_content(chunk_size=8192):
                file.write(chunk)

    return file_name


def updated_file(file, folder_id, admin_url, api_key, app_id, owner='admin'):
    api_method = 'POST'
    url = admin_url + '/api/v1/files/Create'
    image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
    media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
                   ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid', ' midi',
                   ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']
    file_name = file.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                open(file, 'rb'),
                ''
            )
        )
    ]

    headers = {
        'Authorization': auth
    }

    response = requests.request(
        api_method,
        url,
        headers=headers,
        data=payload,
        files=files
    )

    return response


def create_or_update_file(file, folder_id, admin_url, api_key, app_id):
    file_name = file.split('/')[-1]
    # Check if file already exists.
    exists = False
    file_check = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name)
    file_check = file_check.json()
    exist_files = [x['Name'] for x in file_check]

    if file_name in exist_files:
        exists = True

    # Create the file using the OC API.
    if exists:
        response = updated_file(file,
                                folder_id,
                                admin_url,
                                api_key,
                                app_id)
    else:
        response = create_file(file,
                               folder_id,
                               admin_url,
                               api_key,
                               app_id)

    return response


def create_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_data = requests.request('GET', link)
    api_method = 'POST'
    url = admin_url + files_endpoint + files_folder_create
    image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
    media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
                   ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid',
                   ' midi',
                   ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if not folder_id:
        folder_path = ''
        if len(link.split(default_file_path)) > 1:
            path_parts = link.split(default_file_path)[1].split('/')[1:-1]
            folder_shared = 'false'
        else:
            path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
            folder_shared = 'true'
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    headers = {
        'Authorization': auth
    }

    response = requests.request(
        api_method,
        url,
        headers=headers,
        data=payload,
        files=files
    )

    return response


def update_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_data = requests.request('GET', link)
    api_method = 'POST'
    url = admin_url + files_endpoint + files_folder_update
    image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
    media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
                   ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid',
                   ' midi',
                   ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if len(link.split(default_file_path)) > 1:
        path_parts = link.split(default_file_path)[1].split('/')[1:-1]
        folder_shared = 'false'
    else:
        path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
        folder_shared = 'true'
    if not folder_id:
        folder_path = ''
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Get file ID from folder
    folder_files = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name, shared=folder_shared)
    folder_files_data = folder_files.json()
    file_id = folder_files_data[0]['FileId']

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FileId": file_id,
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    headers = {
        'Authorization': auth,
    }

    response = requests.request(
        api_method,
        url,
        headers=headers,
        data=payload,
        files=files
    )

    return response


def create_or_update_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_exists = False
    file_data = requests.request('GET', link)
    api_method = 'POST'
    image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
    media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
                   ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid',
                   ' midi',
                   ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if len(link.split(default_file_path)) > 1:
        path_parts = link.split(default_file_path)[1].split('/')[1:-1]
        folder_shared = 'false'
    else:
        path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
        folder_shared = 'true'
    if not folder_id:
        folder_path = ''
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Get file ID from folder
    folder_files = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name, shared=folder_shared)
    folder_files_data = folder_files.json()

    if len(folder_files_data) > 0:
        file_exists = True
        file_id = folder_files_data[0]['FileId']

    # Build json body to send to API.
    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    if file_exists:
        payload = {
            'json': json.dumps(
                {
                    "FileId": file_id,
                    "FolderId": folder_id,
                    "FileObjectType": object_type,
                    "Owner": owner,
                    "Name": file_name
                }
            )
        }
        url = admin_url + files_endpoint + files_folder_update
    else:
        payload = {
            'json': json.dumps(
                {
                    "FolderId": folder_id,
                    "FileObjectType": object_type,
                    "Owner": owner,
                    "Name": file_name
                }
            )
        }
        url = admin_url + files_endpoint + files_folder_create

    auth = authorize(url, api_key, app_id, method=api_method)
    headers = {
        'Authorization': auth
    }

    response = requests.request(
        api_method,
        url,
        headers=headers,
        data=payload,
        files=files
    )

    return response

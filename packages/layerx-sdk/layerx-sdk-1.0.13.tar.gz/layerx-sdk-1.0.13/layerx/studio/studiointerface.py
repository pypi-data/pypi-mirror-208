import requests


class StudioInterface:

    def __init__(self, auth_token: str, studio_url: str):
        self.auth_token = auth_token
        self.studio_url = studio_url

    ''''
    get selection id from query, filter and collectionId
    '''
    def create_initial_project(self):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/projects/initial/create'

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        except requests.exceptions.RequestException as e:
            print(f"An exception occurred: {format(e)}")
            return {"isSuccess": False}
        except Exception as e1:
            print(f"An exception occurred: {format(e1)}")
            return {"isSuccess": False}

    '''
    update of create project
    '''
    def create_or_update_project(self, project_id, payload, isEditable):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/project/{project_id}/update?isEditable={isEditable}'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False, "message": response.text}
        except requests.exceptions.RequestException as e:
            message = f"An exception occurred: {format(e)}"
            return {"isSuccess": False, "message": message}
        except Exception as e1:
            message = f"An exception occurred: {format(e1)}"
            return {"isSuccess": False, "message": message}

    
    '''
    update of create project
    '''
    def delete_project(self, project_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/project/{project_id}/delete'

        try:
            response = requests.post(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False, "errorMsg": response.text}
        except requests.exceptions.RequestException as e:
            print(f"An exception occurred: {format(e)}")
            return {"isSuccess": False}
        except Exception as e1:
            print(f"An exception occurred: {format(e1)}")
            return {"isSuccess": False}
    

    """
    update the labels of project
    """
    def update_labels_to_project(self, project_id, add_list, remove_list):
        payload = {
            "addList": add_list,
            "removeList": remove_list
        }

        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/project/{project_id}/updateLabel'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        except requests.exceptions.RequestException as e:
            print(f"An exception occurred: {format(e)}")
            return {"isSuccess": False}
        except Exception as e1:
            print(f"An exception occurred: {format(e1)}")
            return {"isSuccess": False}


    """
    Get list of studio project
    """
    def list_projects(self):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/projects/list'

        try:
            response = requests.get(url=url, headers=hed)
            return response.json()
        except requests.exceptions.RequestException as e:
            print("An exception occurred | studio interface, list_projects")
            print(e)

    """
    Update the label group for the project
    """
    def set_project_label_group(self, project_id, group_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.studio_url}/api/client/project/{project_id}/setLabelGroup'
        payload = {
            "labelGroupId": group_id,
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"An exception occurred: {format(e)}")
            return None
        except Exception as e1:
            print(f"An exception occurred: {format(e1)}")
            return None

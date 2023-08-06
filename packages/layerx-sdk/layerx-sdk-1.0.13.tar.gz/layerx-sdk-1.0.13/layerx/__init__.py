import base64
import subprocess

from layerx import datalake, dataset, studio
from layerx.datalake.constants import MediaType, ObjectType

__version__ = '1.0.13'

class LayerxClient:
    """
    Python SDK of LayerX
    """

    def __init__(self, api_key:str, secret: str, layerx_url: str) -> None:
        _string_key_secret = f'{api_key}:{secret}'
        _key_secret_bytes = _string_key_secret.encode("ascii")
        _encoded_key_secret_bytes = base64.b64encode(_key_secret_bytes)
        self.encoded_key_secret = _encoded_key_secret_bytes.decode("ascii")
        self.layerx_url = layerx_url
        self.__check_sdk_version_compatibility()

    def __check_sdk_version_compatibility(self):
        """
        Check if the SDK version is compatible with the datalake backend version
        """
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        version_id = __version__.split('b')[0]

        _datalake_client.check_sdk_version_compatibility(version_id)

    

    def upload_annoations_for_folder(
            self,
            collection_base_path: str,
            operation_unique_id: str,
            json_data_file_path: str,
            shape_type: str,
            is_normalized: bool,
            is_model_run: bool,
            destination_project_id: str = None
    ):
        """
        Upload annotation data from a json file
        """
        # init datalake client
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        if is_model_run:
            _datalake_client.upload_modelrun_from_json(
                collection_base_path,
                operation_unique_id,
                json_data_file_path,
                shape_type,
                is_normalized,
                destination_project_id
            )
        else:
            _datalake_client.upload_groundtruth_from_json(
                collection_base_path,
                operation_unique_id,
                json_data_file_path,
                shape_type,
                is_normalized,
                destination_project_id)

    """
    Download dataset 
    """

    def download_dataset(self, version_id: str, export_type: str, custom_download_path: str = None):
        # init dataset client
        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url, custom_download_path)

        # start download
        _dataset_client.download_dataset(version_id, export_type)

    """"
    Images/video upload - deprecated
    """

    def file_upload(self, path: str, collection_type, collection_name, meta_data_object="", override=False):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.file_upload(path, collection_type, collection_name, meta_data_object, override)

    """"
    Images/video upload to a collection
    @param path: local folder path (absolute)
    @param content_type: 'image' or 'video'
    @param collection_name: Collection which files to be uploaded to. 
    If existing one is given new files are added to that collection
    @param meta_data_object: Object to specify custom meta data fields and flags
    """

    def upload_files_to_collection(
            self, 
            path: str, 
            content_type: str, 
            collection_name: str, 
            meta_data_object={},
            application_code=None):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        if collection_name == "":
            print(f'Invalid collection name "{collection_name}"')
            return {
                "is_success": False,
                "collection_id": None
            }
        if content_type.lower() == "image":
            collection_type = MediaType.IMAGE.value
        elif content_type.lower() == "video":
            collection_type = MediaType.VIDEO.value
        else:
            collection_type = MediaType.OTHER.value

        return _datalake_client.file_upload(path, collection_type, collection_name, meta_data_object, False, application_code)
    
    """"
    trash common logic for sdk 
    @param collection_id: collection id
    @param query: query to filter the objects
    @param filter: filter to filter the objects
    @param object_type: 'image' or 'video'
    @param object_list: list of object ids
    @param is_all_selected: boolean
    """
    def __trash_objects(
        self, 
        collection_id: str, 
        query: str, 
        filter, 
        object_type: int, 
        object_list,
        is_all_selected = True
        ):
        
        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        response = _datalake_client.get_selection_id(collection_id, query, filter, object_type, object_list, is_all_selected)

        print('selection id: ',response)
        get_selection_id_success = True
        if("isSuccess" in response):
            if(response["isSuccess"]== False):
                get_selection_id_success = False
        if(get_selection_id_success):
            selection_id = response['selectionTag']
            return _datalake_client.trash_datalake_object(selection_id)
        else:
            print('trash_response: ',{
                "isSuccess": False
            })
            return {
                "isSuccess": False
            }
        
    """"
    Images/video trash from datalake
    @param datalake_query: query to select objects
    @param datalake_filter: filter to select objects
    @param content_type: 'image' or 'video'
    """
    def trash_objects_from_datalake(
        self, 
        datalake_query: str, 
        datalake_filter = {}, 
        content_type: str = "image", 
        ):
        #print(f'create project using query, filter and collections - project name: {project_name}, ')
        
        #Prevent all objects case
        if datalake_query == "" and (datalake_filter == "" or datalake_filter == {}):
            print('At least either valid filter or query should be given')
            return {
                "is_success": False,
                "error": "Not enough selection parameters"
            }

        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print('No valid content type')
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type"
            }
        try:

            response = self.__trash_objects("", datalake_query, datalake_filter, object_type, [])
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }
    
    """"
    Images/video trash from collection
    @param collection id: collection id
    @param query: query to select objects
    @param filter: filter to select objects
    """
    def trash_objects_from_collection(
        self, 
        collection_id: str, 
        query: str = "", 
        filter = {}, 
        ):

        if(collection_id == None or collection_id == ''):
            print('collection id must be provided')
            return {
                "isSuccess": False,
                "error": 'collection id must be provided'
            }
        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]
        
        if object_type == None:
            print('object type cannot find for collection id')
            return {
                "isSuccess": False,
                "error": 'object type cannot find for collection id'
            }
        
        try:

            response = self.__trash_objects("", query, filter, object_type, [collection_id], False)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "isSuccess": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    Deprecated
    Download collection annotations from datalake
    @param collection_id - id of collection
    @param operation_id - Optional: id of the model (same operation_id given in upload annotations) - default: None
    @param custom_download_path - Optional: custom download path for save downloaded files - default: None
    """
    def download_annotations(self, collection_id: str, operation_id, custom_download_path: str = None):

        print('This method is now deprecated and please switch to "download_collection" function as this will be removed in future')
        # init dataset client
        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url, custom_download_path)

        operation_id_list = []
        if operation_id != None:
            operation_id_list.append(operation_id)
        annotation_type = "all"
        # start download
        _dataset_client.download_annotations(collection_id, annotation_type, operation_id_list)

    
    """
    Download collection annotations from datalake
    @param collection_id - id of collection
    @param annotation_type - Optional: annotation category, can be given ("machine", "human" or "all") - default: "all"
    @param operation_id_list - Optional: id list of the model or ground truth (same operation_id_list given in upload annotations) - default: []
    @param custom_download_path - Optional: custom download path for save downloaded files - default: None
    """

    def download_collection(self, collection_id: str, annotation_type = "all", operation_id_list = [], custom_download_path: str = None):
        # init dataset client
        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url, custom_download_path)

        # start download
        _dataset_client.download_annotations(collection_id, annotation_type, operation_id_list)
    

    """"
    Images and annotation upload
    """
    def upload_data(self, collection_name, file_path, meta_data_object, operation_unique_id, json_data_file_path, shape_type, is_normalized, is_model_run):

        upload_details = None
        if (file_path == None):
            print('file upload cannot be done')
        else:
            upload_details = self.file_upload(file_path, MediaType.IMAGE.value, collection_name, meta_data_object, False)

        if (json_data_file_path == None):
            print('annotation upload cannot be done')
        else:
            job_id = upload_details["job_id"]
            self.wait_for_job_complete(job_id)
            self.upload_annoations_for_folder(collection_name, operation_unique_id, json_data_file_path, shape_type, is_normalized, is_model_run)
        
        return upload_details
    


    """"
    get upload progress
    """

    def get_upload_status(self, collection_name):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.get_upload_status(collection_name)

    """
    remove annotations of collection model run
    """
    def remove_annotations(self, collection_id: str, model_run_id: str):
        print(f'remove annotations of collection: {collection_id}, operation id: {model_run_id}')

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        _datalake_client.remove_collection_annotations(collection_id, model_run_id)


    """
    use to create appropriate filter object from user filter input
    """
    def __create_filter(self, filter):
        #{ "annotation_types": ["human", "raw", "machine"], "from_date": "", "to_date": "" }
        return_filter = {
            "filterBy": [],
            "date": {}
        }
        if "annotation_types" in filter:
            if "human" in filter["annotation_types"]:
                return_filter["filterBy"].append(2)
            if "raw" in filter["annotation_types"]:
                return_filter["filterBy"].append(0)
            if "machine" in filter["annotation_types"]:
                return_filter["filterBy"].append(1)
        if "to_date" in filter:
            return_filter["date"]["toDate"] = filter["to_date"]
        if "from_date" in filter:
            return_filter["date"]["fromDate"] = filter["from_date"]
        return return_filter
    

    """
    create annotation studio project using query, filter and collections
    """
    def __create_studio_project(
        self, 
        project_name: str, 
        collection_id: str, 
        query: str, 
        filter, 
        object_type: int, 
        object_list, 
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        default_shape_type
        ):
        #print(f'create project using query, filter and collections - project name: {project_name}, ')
        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)

        response = _datalake_client.get_selection_id(collection_id, query, filter, object_type, object_list)
        print('selection id: ',response)
        get_selection_id_success = True
        if("isSuccess" in response):
            if(response["isSuccess"] == False):
                get_selection_id_success = False
        if get_selection_id_success == True:
            project_response = _studio_client.create_project(
                project_name, 
                response['selectionTag'], 
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type)
            return project_response
        else:
            print('project_response: ',{
                "isSuccess": False
            })
            return {
                "isSuccess": False
            }
    
    def __get_object_type_by_id(self, object_id: str):
        print(f'get object type by id: {object_id}')

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        response =  _datalake_client.get_object_type_by_id(object_id)
        return response
    

    """
    create annotation studio project using query, filter and collections
    """
    def create_annotation_project_from_collection(
        self, 
        project_name: str, 
        collection_id: str, 
        query: str = "", 
        filter = {}, 
        fps: int = 4,
        frames_per_task: int = 120,
        assign_to_all = False,
        send_email = False,
        default_shape_type = "rectangle"
        ):
        #print(f'create project using query, filter and collections - project name: {project_name}, ')

        if(collection_id == None or collection_id == ''):
            print('collection id must be provided')
            return {
                "isSuccess": False,
                "error": 'collection id must be provided'
            }
        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]
        
        if object_type == None:
            print('object type cannot find for collection id')
            return {
                "isSuccess": False,
                "error": 'object type cannot find for collection id'
            }

        #if((fps == None) and (object_type == ObjectType.VIDEO.value or object_type == ObjectType.VIDEO_COLLECTION.value)):
        #    print('fps must be provided')
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }

        try:
            response = self.__create_studio_project(
                project_name, 
                collection_id, 
                query, 
                filter, 
                0, 
                [], 
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "isSuccess": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    create annotation studio project using query, filter and collections
    """
    def create_annotation_project_from_datalake(
        self, 
        project_name: str, 
        datalake_query: str, 
        datalake_filter = {}, 
        content_type: str = "image", 
        fps: int = 4,
        frames_per_task: int = 120,
        assign_to_all = False,
        send_email = False,
        default_shape_type = "rectangle"
        ):
        #print(f'create project using query, filter and collections - project name: {project_name}, ')
        
        #Prevent all objects case
        if datalake_query == "" and (datalake_filter == "" or datalake_filter == {}):
            print('At least either valid filter or query should be given')
            return {
                "is_success": False,
                "error": "Not enough selection parameters"
            }

        #if(object_type == ObjectType.VIDEO or object_type == ObjectType.VIDEO_COLLECTION):
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }
        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print('No valid content type')
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type"
            }
        try:
            response = self.__create_studio_project(
                project_name, 
                "", 
                datalake_query, 
                datalake_filter,  
                object_type, 
                [], 
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }
    

    """
    update annotation project using query, filter and collections
    """
    def __update_objects_to_studio_project(
        self, 
        project_id: str, 
        collection_id: str, 
        query: str, 
        filter, 
        object_type: int, 
        object_list, 
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        default_shape_type = "rectangle"
        ):
        #print(f'create project using query, filter and collections - project id: {project_id}, ')
        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)

        response = _datalake_client.get_selection_id(collection_id, query, filter, object_type, object_list)
        print('selection id: ',response)
        get_selection_id_success = True
        if("isSuccess" in response):
            if(response["isSuccess"] == False):
                get_selection_id_success = False
        if get_selection_id_success == True:
            project_response = _studio_client.update_project(
                project_id, 
                response['selectionTag'], 
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type
                )
            print('project_response: ',project_response)
            return project_response
        else:
            print('project_response: ',{
                "is_success": False
            })
            return {
                "is_success": False
            }

    """
    update annotation studio project using query, filter and collections
    """
    def add_files_to_annotation_project_from_collection(
        self, 
        project_id: str, 
        collection_id: str, 
        query: str, 
        filter, 
        fps: int = 0,
        frames_per_task: int = 120,
        assign_to_all = False,
        send_email = False,
        default_shape_type = "rectangle"
        ):
        #print(f'create project using query, filter and collections - project name: {project_id}, ')

        if collection_id == None or collection_id == '':
            return {
                "is_success": False,
                "error": 'collection id must be provided'
            }

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]
        
        if object_type == None:
            print('object type cannot find for collection id')
            return {
                "is_success": False,
                "error": 'object type cannot find for collection id'
            }
        #if(fps == None and (object_type == ObjectType.VIDEO.value or object_type == ObjectType.VIDEO_COLLECTION.value)):
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }

        try:
            response = self.__update_objects_to_studio_project(
                project_id, 
                collection_id, 
                query, 
                filter, 
                0, 
                [], 
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    update annotation studio project using query, filter and collections
    """
    def add_files_to_annotation_project_from_datalake(
        self, 
        project_id: str, 
        query: str, 
        filter, 
        content_type: str, 
        fps: int = 0,
        frames_per_task: int = 120,
        assign_to_all = False,
        send_email = False,
        default_shape_type = "rectangle"
        ):
        #print(f'create project using query, filter and collections - project name: {project_id}, ')

        if query == "" and (filter == "" or filter == {}):
            print('At least either valid filter or query should be given')
            return {
                "is_success": False,
                "error": "Not enough selection parameters"
            }

        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print('No valid content type')
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type"
            }
        try:
            response = self.__update_objects_to_studio_project(
                project_id, 
                "", 
                query, 
                filter, 
                object_type, 
                [], 
                fps, 
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }
    """
    delete a annotation studio project by project id
    """
    def delete_annotation_project(self, project_id: str):
        if(project_id == None or project_id == ""):
            print("Project id not valid")
            return {
                "is_success": False,
                "error": f'Project id not available'
            }
        print(f'delete project - project id: {project_id}')
        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)
        try:
            response = _studio_client.delete_project(project_id)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    update the labels of studio project
    """
    def __update_labels_to_studio_project(self, project_id: str, add_list, remove_list):
        #print(f'add labels to project - project id: {project_id}, add label list: {add_list}, remove label list: {remove_list}')

        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)

        response = _studio_client.update_labels_to_project(project_id, add_list, remove_list)

        return response
    
    """
    add the labels of studio project
    """
    def add_labels_to_studio_project(self, project_id: str, add_list):
        print(f'add labels to project - project id: {project_id}, label list: {add_list}')
        try:
            response =  self.__update_labels_to_studio_project(project_id, add_list, [])
            print('response: ', response)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    remove the labels of studio project
    """
    def remove_labels_to_studio_project(self, project_id: str, remove_list):
        print(f'remove labels to project - project id: {project_id}, label list: {remove_list}')

        try:
            response =  self.__update_labels_to_studio_project(project_id, [], remove_list)
            print('response: ', response)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {
                "is_success": False,
                "error": f'An exception occurred: {format(e)}'
            }

    """
    Get list of studio project
    """
    def get_annotation_project_list(self):
        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)
        return _studio_client.studio_project_list()
    

    """
    create dataset from search objects
    create dataset from search objects
    @param dataset_name - name of the dataset
    @param collection_id - collection_id for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @param object_type - object_type for search objects
    @param object_list - object_list for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def __create_dataset(
        self, 
        dataset_name: str, 
        collection_id: str, 
        query: str, 
        filter, 
        object_type, 
        object_list, 
        split_nfo, 
        labels, 
        export_types,
        operation_list,
        augmentation_list):
        print(f'create dataset - dataset name: {dataset_name}')

        if dataset_name == "" or dataset_name == None:
            print(f'Invalid dataset name "{dataset_name}"')
            return {
                "is_success": False,
                "error": "Invalid dataset name"
            }
        if object_type.lower() == "image":
            object_type = ObjectType.IMAGE.value
        elif object_type.lower() == "image_collection":
            object_type = ObjectType.IMAGE_COLLECTION.value
        elif object_type.lower() == "dataset":
            object_type = ObjectType.DATASET.value
        else:
            print("Invalid content type - should be either 'image'")
            return {
                "is_success": False,
                "collection_id": None
            }

        filter = self.__create_filter(filter)

        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url)

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        response = _datalake_client.get_selection_id(collection_id, query, filter, object_type, object_list)
        print('selection id: ',response)
        get_selection_id_success = True
        if("isSuccess" in response):
            if(response["isSuccess"] == False):
                get_selection_id_success = False
        if get_selection_id_success == True:
            dataset_response = _dataset_client.create_dataset(
                dataset_name, 
                response['selectionTag'], 
                split_nfo, 
                labels, 
                export_types, 
                operation_list,
                augmentation_list)
            print('dataset_response: ',dataset_response)
            return dataset_response
        else:
            print('dataset_response: ',{
                "isSuccess": False
            })
            return {
                "isSuccess": False
            }


    """
    create dataset from search objects on collection
    @param dataset_name - name of the dataset
    @param collection_id - collection_id for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def create_dataset_from_collection(
        self, 
        dataset_name: str, 
        collection_id: str, 
        split_info, 
        labels = [], 
        export_types = [],
        query: str = "", 
        filter = {},
        operation_list = None,
        augmentation_list = None):

        if(collection_id == None):
            return {
                "isSuccess": False,
                "error": 'collection id must be provided'
            }

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]
        
        if object_type == None:
            print('object type cannot find for collection id')
            return {
                "isSuccess": False,
                "error": 'object type cannot find for collection id'
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            object_type = "image"
        else:
            return {
                "isSuccess": False,
                "error": 'collection type is not acceptable for create dataset, only image collections are valid'
            }

        return self.__create_dataset(
            dataset_name, 
            collection_id, 
            query, 
            filter, 
            object_type, 
            [], 
            split_info, 
            labels, 
            export_types, 
            operation_list,
            augmentation_list)

    

    """
    create dataset from search objects on datalake
    @param dataset_name - name of the dataset
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param content_type - content_type for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def create_dataset_from_datalake(
        self, 
        dataset_name: str,
        split_info,
        labels = [], 
        export_types = [],
        item_type = "image",
        query: str = "", 
        filter = {},
        operation_list = None,
        augmentation_list = None):
            
        return self.__create_dataset(
            dataset_name, 
            None, 
            query, 
            filter, 
            item_type, 
            [], 
            split_info, 
            labels, 
            export_types, 
            operation_list,
            augmentation_list)

    

    """
    update dataset from search objects
    @param version_id - id of the base version
    @param collection_id - collection_id for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @param object_type - object_type for search objects
    @param object_list - object_list for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def __update_dataset_version(
        self, 
        version_id: str, 
        collection_id: str, 
        query: str, 
        filter, 
        object_type, 
        object_list, 
        split_info, 
        labels, 
        export_types,
        is_new_version_required,
        operation_list,
        augmentation_list):
        print(f'create dataset - dataset version id: {version_id}')

        if object_type.lower() == "image":
            object_type = ObjectType.IMAGE.value
        elif object_type.lower() == "image_collection":
            object_type = ObjectType.IMAGE_COLLECTION.value
        elif object_type.lower() == "dataset":
            object_type = ObjectType.DATASET.value
        else:
            print("Invalid content type - should be either 'image'")
            return {
                "is_success": False
            }

        filter = self.__create_filter(filter)

        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url)

        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)

        response = _datalake_client.get_selection_id(collection_id, query, filter, object_type, object_list)
        print('selection id: ',response)
        get_selection_id_success = True
        if("isSuccess" in response):
            if(response["isSuccess"] == False):
                get_selection_id_success = False
        if get_selection_id_success == True:
            dataset_response = _dataset_client.update_dataset_version(
                version_id, 
                response['selectionTag'], 
                split_info, 
                labels, 
                export_types, 
                is_new_version_required, 
                operation_list,
                augmentation_list)
            print('dataset_response: ',dataset_response)
            return dataset_response
        else:
            print('dataset_response: ',{
                "isSuccess": False
            })
            return {
                "isSuccess": False
            }


    """
    update dataset from search objects on collection
    @param version_id - id of the base version
    @param collection_id - collection_id for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def update_dataset_version_from_collection(
        self, 
        version_id: str, 
        collection_id: str, 
        split_info, 
        labels = [], 
        export_types = [],
        query: str = "", 
        filter = {},
        is_new_version_required = False,
        operation_list = None,
        augmentation_list = None):

        if(collection_id == None or collection_id == ""):
            return {
                "isSuccess": False,
                "error": 'collection id must be provided'
            }
        if(version_id == None or version_id == ""):
            return {
                "isSuccess": False,
                "error": 'version id must be provided'
            }

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]
        
        if object_type == None:
            print('object type cannot find for collection id')
            return {
                "isSuccess": False,
                "error": 'object type cannot find for collection id'
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            object_type = "image"
        else:
            return {
                "isSuccess": False,
                "error": 'collection type is not acceptable for create dataset, only image collections are valid'
            }

        return self.__update_dataset_version(
            version_id, 
            collection_id, 
            query, 
            filter, 
            object_type, 
            [], 
            split_info, 
            labels, 
            export_types, 
            is_new_version_required, 
            operation_list,
            augmentation_list)

    

    """
    update dataset from search objects on datalake
    @param version_id - id of the base version
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param item_type - content_type for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - { 
        "annotation_types": ["human", "raw", "machine"], 
        "from_date": "", "to_date": "" 
    }
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """
    def update_dataset_version_from_datalake(
        self, 
        version_id: str,  
        split_info, 
        labels = [], 
        export_types = [],
        item_type: str = "image",
        query: str = "", 
        filter = {},
        is_new_version_required = False,
        operation_list = None,
        augmentation_list = None):
        
        if(version_id == None or version_id == ""):
            return {
                "isSuccess": False,
                "error": 'version id must be provided'
            }
        return self.__update_dataset_version(
            version_id, 
            None, 
            query, 
            filter, 
            item_type, 
            [], 
            split_info, 
            labels, 
            export_types, 
            is_new_version_required, 
            operation_list,
            augmentation_list)

    

    """
    delete dataset version
    @param version_id - id of the deleting version
    """
    def delete_dataset_version(self, version_id: str):
        print(f'delete dataset version - dataset version id: {version_id}')

        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url)
        response = _dataset_client.delete_dataset_version(version_id)
        print(response)
        return response



    


    

    """
    Get list of all system labels
    """
    def get_all_labels(self):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.get_system_labels()

    """
    Get list of system labels that attached to given group
    """
    def get_labels_in_group(self, group_id):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.get_system_labels(group_id)

    """
    Create a group from labels (label keys)
    """
    def create_label_group(self, group_name, label_ids):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.create_label_group(group_name, label_ids)

    """
    Attach labels to a group
    """
    def attach_labels_to_group(self, group_id, label_ids):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.attach_labels_to_group(group_id, label_ids)
    
    """
    Detach labels from group
    """
    def detach_labels_from_group(self, group_id, label_ids):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.detach_labels_from_group(group_id, label_ids)

    """
    List All label groups
    """
    def get_all_label_groups(self):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.get_all_label_groups()

    """
    Attach label group to annotation project
    """
    def attach_label_group_to_annotation_project(self, project_id, group_id):
        _studio_client = studio.StudioClient(self.encoded_key_secret, self.layerx_url)
        return _studio_client.project_set_label_group(project_id, group_id)


    """
    Deprecated
    Download project annotations
    @param project_id - id of annotation project
    @param task_status_list - (Optional): To filter by task status - default: []
    @param is_annotated_only - (Optional): If True, then only the annotated images are downloaded - default: False
    @param custom_download_path - (Optional): To download data to required location instead of current directory - default: None
    """

    def download_project_annotations(self, project_id, task_status_list: list = [], is_annotated_only: bool = False, custom_download_path: str = None):

        print('This method is now deprecated and please switch to "download_annotation_projects" function as this will be removed in future')
        # init dataset client
        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url, custom_download_path)

        project_id_list = []
        project_id_list.append(project_id)
        # start download
        _dataset_client.download_annotations_for_project_v2(project_id_list, task_status_list, is_annotated_only)

    

    """
    Download multiple project annotations
    @param project_id_list - id list of annotation projects
    @param task_status_list - (Optional): To filter by task status - default: []
    @param is_annotated_only - (Optional): If True, then only the annotated images are downloaded - default: False
    @param custom_download_path - (Optional): To download data to required location instead of current directory - default: None
    """

    def download_annotation_projects(self, project_id_list, task_status_list: list = [], is_annotated_only: bool = False, custom_download_path: str = None):

        if task_status_list == None:
            task_status_list = []

        # init dataset client
        _dataset_client = dataset.DatasetClient(self.encoded_key_secret, self.layerx_url, custom_download_path)

        # start download
        _dataset_client.download_annotations_for_project_v2(project_id_list, task_status_list, is_annotated_only)


    
    """
    Wait until job complete
    @param job_id - id of the relevant job
    """
    def wait_for_job_complete(self, job_id: str):
        _datalake_client = datalake.DatalakeClient(self.encoded_key_secret, self.layerx_url)
        return _datalake_client.wait_for_job_complete(job_id)
    
    
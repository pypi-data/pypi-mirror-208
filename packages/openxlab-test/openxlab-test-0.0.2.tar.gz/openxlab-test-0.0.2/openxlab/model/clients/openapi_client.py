import requests

from openxlab.model.common.constants import paths
from openxlab.model.common.response_dto import ReturnDto
from openxlab.model.common.meta_file_util import get_meta_payload, get_filename_from_url
import os
from openxlab.xlab.handler.user_token import get_jwt


class OpenapiClient(object):
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token

    # def get_dataset_files(self, dataset_name:str, prefix:str):
    def get_download_url(self, repository, file):
        """
        get file(model file|meta file|log file|readme file) download url
        """
        client_from = os.environ.get('CLIENT_FROM', '0')
        payload = {"repositoryName": repository, "fileName": file, "clientFrom": client_from}
        path = paths['file_download_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Get download url error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Get download url error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data['data']['url'], response_dto.data['data']['fileName'], \
            response_dto.data['data']['hash'], response_dto.data['data']['weightRawSize']

    def get_metafile_template_download_url(self, file=None):
        """
        get metafile template download url
        """
        payload = {}
        path = paths['meta_file_template_download_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Get download url error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Get download url error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data['data']['url']

    def create_repository(self, repository: str, private: bool, meta_data: dict):
        """
        create repository
        """
        payload = get_meta_payload(repository, private, meta_data)
        path = paths['create_repository_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Create repository error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Create repository error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data

    def update_repository(self, repository: str, private: bool):
        """
        update repository
        """
        public_status = 0 if private else 1
        payload = {"repoName": repository, "publicStatus": public_status}
        path = paths['update_repository_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Create repository error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Create repository error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data

    def remove_repository(self, repository):
        """
        remove repository
        """
        payload = {"repoName": repository}
        path = paths['delete_repository_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Create repository error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Create repository error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data

    def query_models(self, repository, metafile=None):
        """
        query models
        """
        payload = {"repoName": repository}
        path = paths['query_models_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Create repository error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Create repository error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data['data']

    def update_upload_status(self, repository, file_names, new_models=None, update_models=None, upload_status=None):
        """
        update upload status
        """
        _new_models = None
        if new_models is not None:
            _new_models = [{"name": m['Name'], "weightName": get_filename_from_url(m['Weights']),
                            "evaluations": [{"task": e['Task'], "dataset": e['Dataset']} for e in m['Results']]} for m
                           in new_models]
        payload = {"repoName": repository, "fileNames": file_names, "uploadStatus": upload_status,
                   "models": _new_models}
        path = paths['update_upload_status_path']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Update upload status error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Update upload status error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data['data']

    def get_upload_signature(self, repository_id, uid, model, model_info):
        payload = {"tag": "file", "key": "model-center", "type": 0, "fileType": "file/pth",
                   "fileName": model_info['objectName'],
                   "data": {"repositoryId": repository_id, "modelId": model_info['modelId'],
                            "modelName": model_info['modelName'], "weightName": model_info['weightName'],
                            "uid": uid}}
        path = paths['get_upload_signature']
        response_dto = self.http_post_response_dto(path, payload)
        if response_dto.msg_code != '10000':
            raise ValueError(f"Get upload signature error:{response_dto.msg}, traceId:{response_dto.trace_id}")
        if response_dto.data['msgCode'] != '10000':
            raise ValueError(f"Get upload signature error:{response_dto.data['msg']}, "
                             f"traceId:{response_dto.data['traceId']}")
        return response_dto.data['data']

    def http_post_response_dto(self, path, payload):
        headers = self.http_common_header()
        print(f"headers:{headers}, body:{payload}")
        response = requests.post(f"{self.endpoint}{path}", json=payload, headers=headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dto = ReturnDto.from_camel_case(response_dict)
        return response_dto

    def http_common_header(self):
        try:
            jwt = get_jwt()
        except ValueError as e:
            print(f"Error: {e}")
            return
        header_dict = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": jwt
        }
        return header_dict

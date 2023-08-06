import base64
import re
import time

from layerx.datalake.annotation import Annotation
from layerx.datalake.query import Query

from .ground_truth import GroundTruth
from .constants import BOX_ANNOTATION, POLYGON_ANNOTATION, LINE_ANNOTATION, MediaType, JobStatus
from .datalakeinterface import DatalakeInterface
from .file_upload import FileUpload
from .file_trash import FileTrash
from .logger import get_debug_logger
from .model_run import ModelRun

datalake_logger = get_debug_logger('DatalakeClient')


class DatalakeClient:
    """
    Python SDK of Datalake
    """

    def __init__(self, encoded_key_secret: str, layerx_url: str) -> None:
        _datalake_url = f'{layerx_url}/datalake' #/datalake :3000
        self.datalake_interface = DatalakeInterface(encoded_key_secret, _datalake_url)

    def check_sdk_version_compatibility(self, sdk_version: str):
        """
        check sdk version compatibility
        """

        if re.compile(r'^(\d+\.)+\d+$').match(sdk_version) is None:
            raise Exception('sdk_version is invalid format')

        if sdk_version is None or sdk_version == '' :
            raise Exception('sdk_version is None')
        
        res = self.datalake_interface.check_sdk_version_compatibility(sdk_version)

        if res["isCompatible"] == False:
            raise Exception(res["message"])

    def upload_annotation_from_cocojson(self, file_path: str):
        """
        available soon
        """
        datalake_logger.debug(f'file_name={file_path}')
        _annotation = GroundTruth(client=self)
        _annotation.upload_coco(file_path)

    def upload_modelrun_from_json(
            self,
            storage_base_path: str,
            model_id: str,
            file_path: str,
            annotation_geometry: str,
            is_normalized: bool,
            dest_project_id: str
    ):
        datalake_logger.debug(f'upload_modelrun_from_json file_path={file_path}, '
                              f'annotation_geometry={annotation_geometry}')
        _model = ModelRun(client=self)
        if annotation_geometry == BOX_ANNOTATION:
            _model.upload_modelrun_json(storage_base_path, model_id, file_path, BOX_ANNOTATION, is_normalized, dest_project_id)
        elif annotation_geometry == POLYGON_ANNOTATION:
            _model.upload_modelrun_json(storage_base_path, model_id, file_path, POLYGON_ANNOTATION, is_normalized, dest_project_id)
        elif annotation_geometry == LINE_ANNOTATION:
            _model.upload_modelrun_json(storage_base_path, model_id, file_path, LINE_ANNOTATION, is_normalized, dest_project_id)
        else:
            datalake_logger.debug(f'unsupported annotation_geometry={annotation_geometry}')

    def upload_groundtruth_from_json(
            self,
            storage_base_path: str,
            operation_id: str,
            file_path: str,
            annotation_geometry: str,
            is_normalized: bool,
            dest_project_id: str
    ):
        datalake_logger.debug(f'upload_groundtruth_from_json file_path={file_path}, '
                              f'annotation_geometry={annotation_geometry}')
        _groundTruth = GroundTruth(client=self)
        if annotation_geometry == BOX_ANNOTATION:
            _groundTruth.upload_groundtruth_json(storage_base_path, operation_id, file_path, BOX_ANNOTATION, is_normalized, dest_project_id)
        elif annotation_geometry == POLYGON_ANNOTATION:
            _groundTruth.upload_groundtruth_json(storage_base_path, operation_id, file_path, POLYGON_ANNOTATION, is_normalized, dest_project_id)
        elif annotation_geometry == LINE_ANNOTATION:
            _groundTruth.upload_groundtruth_json(storage_base_path, operation_id, file_path, LINE_ANNOTATION, is_normalized, dest_project_id)
        else:
            datalake_logger.debug(f'unsupported annotation_geometry={annotation_geometry}')

    def file_upload(self, path: str, collection_type, collection_name, meta_data_object, override, application_code):
        _upload = FileUpload(client=self, application_code=application_code)
        upload_res = _upload.file_upload_initiate(path, collection_type, collection_name, meta_data_object, override)
        return upload_res

    def get_upload_status(self, collection_name):
        _upload = FileUpload(client=self)
        return _upload.get_upload_status(collection_name)

    def remove_collection_annotations(self, collection_id: str, model_run_id: str):
        print(f'annotation delete of collection ={collection_id}', f'model id={model_run_id}')
        _model = Annotation(client=self)
        _model.remove_collection_annotations(collection_id, model_run_id)


    """
    get selection id for query, collection id, filter data
    """
    def get_selection_id(self, collection_id, query, filter, object_type, object_list, is_all_selected=True):
        _query = Query(client=self)
        response = _query.get_selection_id(collection_id, query, filter, object_type, object_list, is_all_selected)
        return response


    def get_object_type_by_id(self, object_id):
        response = self.datalake_interface.get_object_type_by_id(object_id)
        return response

    def get_system_labels(self, group_id = None):
        response = self.datalake_interface.get_all_label_list(group_id)
        return response

    def attach_labels_to_group(self, group_id, label_keys):
        if group_id == '' or len(label_keys) == 0:
            print('Label group id or label list is empty')
            return { "is_success": False}
        response = self.datalake_interface.add_labels_to_group(group_id, label_keys)
        return response

    def detach_labels_from_group(self, group_id, label_keys):
        if group_id == '' or len(label_keys) == 0:
            print('Label group id or label list is empty')
            return { "is_success": False}
        response = self.datalake_interface.remove_labels_from_group(group_id, label_keys)
        return response

    def get_all_label_groups(self):
        response = self.datalake_interface.get_all_group_list()
        return response

    def create_label_group(self, group_name, label_keys):
        if group_name == '' or len(label_keys) == 0:
            print('Label group name or label list is empty')
            return None
        response = self.datalake_interface.create_label_group(group_name, label_keys)
        return response

    def wait_for_job_complete(self, job_id):
        print(f"Waiting until complete the job: {job_id}")
        while True:
            try:
                job_detils = self.datalake_interface.check_job_status(job_id)

                if job_detils["isSuccess"]:
                    job_status = job_detils["status"]
                    job_progress = job_detils["progress"]
                    print(f'Job progress: {job_progress}')
                    if job_status == JobStatus.COMPLETED.value:
                        res = {
                            "is_success" : True,
                            "job_status" : "COMPLETED"
                        }
                        print(res)
                        return res
                    elif job_status == JobStatus.FAILED.value:
                        res = {
                            "is_success" : True,
                            "job_status" : "COMPLETED"
                        }
                        print(res)
                        return res
                    else:
                        time.sleep(30)
                else:
                    res = {
                        "is_success": False,
                        "job_status": "FAILED"
                    }
                    print(res)
                    return res
            except Exception as e:
                print(f"An exception occurred: {format(e)}")
                res = {
                    "is_success": False,
                    "job_status": "FAILED"
                }
                print(res)
                return res
    
    """
    trash selection object
    """
    def trash_datalake_object(self, selection_id):
        _trash = FileTrash(client=self)
        return _trash.trash_files(selection_id)

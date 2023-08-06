from layerx.datalake.s3_interface import S3Interface


class S3Upload:

    def __init__(self, client, collection_name, upload_id, test_write_progress, add_fail_files, application_code):
        self._client = client
        self.collectionName = collection_name
        self.uploadId = upload_id
        self.write_progress = test_write_progress
        self.add_fail_files = add_fail_files
        self.application_code = application_code
        self.file_id = ""
        self.file_key = ""

    """"
    Initialize multipart upload
    """

    def initialize_multipart_upload(self, file_name: str):
        payload = {
            "fileName": file_name,
            "collectionName": self.collectionName,
            "uploadId": self.uploadId,
            "applicationCode": self.application_code
        }
        multipart_init_res = self._client.datalake_interface.get_file_id_and_key(payload)
        return multipart_init_res

    """"
    Multipart upload
    """

    def multi_part_upload(self, sub_list):

        for file in sub_list:
            '''Get file id and key'''
            multipart_init_res = self.initialize_multipart_upload(file["key"])

            if multipart_init_res["isSuccess"]:
                self.file_id = multipart_init_res["fileId"]
                self.file_key = multipart_init_res["fileKey"]
                #If isExisting is present and is true, then skip all operations to file because its already uploaded to datalake
                if "isExisting" in multipart_init_res and multipart_init_res["isExisting"]:
                    self.write_progress()
                    print(f'\nFile {self.file_key} already exists in datalake. Skipping upload')
                    continue
            else:
                self.add_fail_files(file["key"])
                continue

            pre_signed_url_pay_load = {
                "fileId": self.file_id,
                "fileKey": self.file_key,
                "parts": 1
            }

            """"Get pre signed url"""
            pre_signed_url_response = self._client.datalake_interface.get_pre_signed_url(pre_signed_url_pay_load)

            if pre_signed_url_response["isSuccess"]:
                url_array = pre_signed_url_response["parts"]
            else:
                self.add_fail_files(file["key"])
                continue

            for part in url_array:

                s3_interface = S3Interface()

                """"Upload s3 file"""
                upload_s3_response = s3_interface.upload_to_s3(part["signedUrl"], file["path"])

                if not upload_s3_response["isSuccess"]:
                    self.add_fail_files(file["key"])
                    continue

                finalize_payload = {
                    "fileId": self.file_id,
                    "fileKey": self.file_key,
                    "parts": [
                        {
                            "PartNumber": 1,
                            "ETag": upload_s3_response["e_tag"]
                        }
                    ],
                    "uploadId": self.uploadId
                }

                """"Finalize multipart upload"""
                finalize_re = self._client.datalake_interface.finalize_upload(finalize_payload)

                if finalize_re["isSuccess"]:
                    self.write_progress()

                else:
                    self.add_fail_files(file["key"])
                    continue

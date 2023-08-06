import json
import os
import tempfile
from http import HTTPStatus

import backoff
import requests

from .exceptions import (
    ConstellationException,
    ConstellationInvalidMethodException,
    ConstellationInvalidResponseException,
    ConstellationMissingFieldException,
    ConstellationNotLoggedInException,
    ConstellationObjectDoesNotExistException,
)
from .models import ConstellationFieldParser


class Constellation:
    def __init__(self, auth_token="", host=""):
        self._host = host or "https://constellation.emeraldcloudlab.com"
        self._auth_token = auth_token

        self._temp_directory = None

    # Retry decorator for requests failures (like timeout or connection error)
    _retry_requests_decorator = backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_tries=5,
    )

    # Configuration related functions
    def host(self):
        """Return the url of the instance constellation that the client is connecting to"""
        return self._host

    def download_directory(self):
        """Returns where cloud file downloads are stored"""
        if self._temp_directory is None:
            self._temp_directory = tempfile.TemporaryDirectory()

        return self._temp_directory.name

    # Identity requests
    @_retry_requests_decorator
    def login(self, username, password):
        """Return the auth token token for the supplied username and password"""
        auth_token = self._send_and_validate_request(
            "/ise/signintoken",
            {"username": username, "password": password},
            "AuthToken",
            requires_auth_token=False,
        )
        self.set_auth_token(auth_token)
        return self.me()

    def is_logged_in(self):
        return self._auth_token != ""

    def set_auth_token(self, auth_token):
        """Set the auth token used by the constellation client"""
        self._auth_token = auth_token

    @_retry_requests_decorator
    def me(self):
        """Return the response from the /ise/me endpoint"""
        return self._send_and_validate_request("/ise/me", None, None, method="GET")

    # Searching objects
    def search(self, ecl_type, query):
        """Perform a simple search on a given type"""
        payload = {
            "queries": [
                {
                    "clauses": [
                        {
                            "Types": [ecl_type],
                            "Query": query,
                        }
                    ],
                    "SubTypes": True,
                    "date": None,
                    "ignore_time": False,
                }
            ],
        }

        return self._send_and_validate_request(
            "/obj/search",
            payload,
            field_to_retrieve="Results",
        )

    # Downloading objects
    def download(self, objects, field_string="All", auto_download_cloud_files=False):
        """Download the supplied fields off the supplied object or objects.

        Note that fields can traverse across links using []'s.  For example:

        download(self.me()["ID"], "FinancingTeams[Name]")

        will download the status field off the protocol link of the supplied
        object.
        """
        result = None
        collapse_fields = False
        collapse_objects = False

        # Normalize the object and fields so they're always lists,
        # even if they're passed as single things.  This allows to
        # handle things like download("obj1", "Name") and
        # download([obj1], ["Name"]) in the same interface
        if not isinstance(field_string, list):
            field_string = [field_string]
            collapse_fields = True

        if not isinstance(objects, list):
            objects = [objects]
            collapse_objects = True

        result = self._download_objects(
            objects, field_string, auto_download_cloud_files
        )

        # Unwind the normalization of fields and object ids into lists
        if collapse_fields and collapse_objects:
            return result[0][0]
        if collapse_fields:
            return [x[0] for x in result]
        if collapse_objects:
            return result[0]

        return result

    def _download_objects(self, objects, field_string, auto_download_cloud_files):
        """Download multiple objects in a single request"""

        # Build the request
        traversals = self._parse_download_field_string(field_string)
        obj_requests = []
        for obj in objects:
            obj_request = {"object": {"id": obj.id}, "limit": 0, "subfield_info": True}
            if traversals:
                obj_request["traversals"] = traversals
            obj_requests.append(obj_request)

        # Send the request to constellation
        responses = self._send_and_validate_request(
            "/obj/download",
            {"requests": obj_requests},
            "responses",
        )
        if len(responses) != len(objects):
            raise ConstellationInvalidResponseException(
                "Expected exactly {} response from /obj/download".format(len(objects)),
                responses,
            )

        # Parse the json results into objects
        response_objects = {}
        field_parser = ConstellationFieldParser(self.download_blob_ref)
        for response in responses:
            (
                sub_response_objects,
                sub_response_field_summaries,
            ) = self._parse_field_values_from_response(response)
            response_objects.update(sub_response_objects)
            for ecl_type, field_summaries in sub_response_field_summaries.items():
                field_parser.add_summaries_for_type(field_summaries, ecl_type)

        # Map the objects into a formatted result based on the fields string
        parsed_results = self._parse_results_from_response(
            response_objects, objects, traversals, field_parser
        )

        # If requested, go ahead and download all the cloud files encountered
        if auto_download_cloud_files:
            for cloud_file in field_parser.cloud_files_encountered():
                self.download_cloud_file(cloud_file)

        # return the results
        return parsed_results

    def _parse_field_values_from_response(self, response):
        """Parse out the field values contained in the response"""
        response_objects = {}
        field_summaries = {}
        response_fields = response.get("fields", {})
        response_field_summaries = response.get("summaries", {})
        ecl_type = response.get("resolved_object", {}).get("type")
        object_id = response.get("resolved_object", {}).get("id")

        if ecl_type is None or object_id is None:
            raise ConstellationObjectDoesNotExistException(
                response.get("object", {}).get("id")
            )

        response_objects[object_id] = {"type": ecl_type, "id": object_id}
        response_objects[object_id].update(response_fields)
        if ecl_type not in field_summaries:
            field_summaries[ecl_type] = {}
        field_summaries[ecl_type].update(response_field_summaries)
        for traversed_object in response.get("traversed_objects", []):
            (
                traversed_response_objects,
                traversed_field_summaries,
            ) = self._parse_field_values_from_response(traversed_object)
            response_objects.update(traversed_response_objects)
            field_summaries.update(traversed_field_summaries)

        return response_objects, field_summaries

    def _parse_download_field_string(self, field_string):
        """Parse the download field string into fields and traversals for constellation"""
        return [
            self._parse_traversal_from_field_string(traversal_string)
            for traversal_string in field_string
        ]

    def _parse_traversal_from_field_string(self, field_string):
        """Parse a download traversal from the string format.

        E.g., turn FinancingTeams[Name] -> constellation consumable traversal
        """
        tokens = field_string.split("[", 1)
        if len(tokens) == 0:
            return None

        current_traversal = {"name": tokens[0].replace("]", "")}
        if len(tokens) == 1:
            return current_traversal

        current_traversal.update(
            {"next": [self._parse_traversal_from_field_string(tokens[1])]}
        )
        return current_traversal

    def _parse_results_from_response(
        self, response_objects, objects, traversals, field_parser
    ):
        """Parse out the response for the requested fields and traversals"""
        results = []
        for obj in objects:
            results.append(
                self._parse_results_from_traversals(
                    response_objects, obj, traversals, field_parser
                )
            )
        return results

    def _parse_results_from_traversals(
        self, objects_info, obj, traversals, field_parser
    ):
        """Parse out the response for the requested traversals"""
        object_info = objects_info.get(obj.id, {})
        results = []
        for traversal in traversals:
            if "name" not in traversal:
                continue
            field_name = traversal["name"]
            field_value = object_info.get(field_name)
            if field_name == "All":
                all_dict = {}
                for field_name, field_value in object_info.items():
                    all_dict[field_name] = field_parser.parse_field_value(
                        object_info.get("type"), field_name, field_value
                    )
                return [all_dict]

            if "next" in traversal:
                sub_traversals = traversal["next"]
                if isinstance(field_value, list):
                    results.append(
                        [
                            self._parse_results_from_traversals(
                                objects_info,
                                field_parser.to_link(field_obj),
                                sub_traversals,
                                field_parser,
                            )
                            for field_obj in field_value
                        ][0]
                    )
                else:
                    results.append(
                        self._parse_results_from_traversals(
                            objects_info,
                            field_parser.to_link(field_value),
                            sub_traversals,
                            field_parser,
                        )[0]
                    )
            else:
                results.append(
                    field_parser.parse_field_value(
                        object_info.get("type"), field_name, field_value
                    )
                )

        return results

    # Downloading cloud files
    def download_cloud_file(self, cloud_file):
        """Download the supplied cloud file to client.download_directory()"""
        file_name, extension, file_info = self.download(
            cloud_file, ["FileName", "FileType", "CloudFile"]
        )
        extension = extension.replace('"', "")
        if not file_name:
            file_name = "EmeraldCloudFile_{}".format(cloud_file.id.replace(":", "_"))
        target_path = self._get_temp_file_path(file_name, extension)
        target_path = self._download_cloud_file(
            file_info["CloudFileId"], file_info["Bucket"], file_info["Key"], target_path
        )

        cloud_file.local_path = target_path
        return target_path

    def _get_temp_file_path(self, filename, extension):
        """Get a temp file path as close to filename as possible"""
        index = 0
        target_path = os.path.join(
            self.download_directory(), filename + "." + extension
        )
        while os.path.exists(target_path):
            target_path = os.path.join(
                self.download_directory(), filename + "_{}.".format(index) + extension
            )
            index += 1

        return target_path

    def blobsign_download(self, cloud_file_id, cloud_file_bucket, cloud_file_key):
        """Return the url to download the supplied cloud file"""
        return self._send_and_validate_request(
            "/blobsign/download",
            {
                "CloudFileId": cloud_file_id,
                "Bucket": cloud_file_bucket,
                "Key": cloud_file_key,
            },
            "Url",
        )

    def _download_cloud_file(
        self, cloud_file_id, cloud_file_bucket, cloud_file_key, target_path
    ):
        """Download a cloud file based off the supplied identifiers"""
        url = self.blobsign_download(cloud_file_id, cloud_file_bucket, cloud_file_key)
        if not url:
            raise ConstellationMissingFieldException(
                "When downloading cloud file", "url"
            )

        # Now download the file from s3
        target_file = open(target_path, "wb")
        download_response = requests.get(url)
        target_file.write(download_response.content)
        target_file.close()

        return target_path

    def download_blob_ref(self, blob_ref, target_path=""):
        """Download a blob ref to the supplied target path"""
        target_path = target_path or self._get_temp_file_path(blob_ref.file_hash, "tmp")

        cloud_file_bucket = blob_ref.bucket
        cloud_file_key = blob_ref.key()
        if not cloud_file_bucket:
            raise ConstellationMissingFieldException(
                "When downloading cloud file", "bucket"
            )
        if not cloud_file_key:
            raise ConstellationMissingFieldException(
                "When downloading cloud file", "hash"
            )

        target_path = self._download_cloud_file(
            "", cloud_file_bucket, cloud_file_key, target_path
        )
        blob_ref.local_path = target_path
        return target_path

    # Uploading objects
    def upload(self, object_type, object_id, new_field_values):
        """Performs a very simple upload of a list of fields on a single object.

        Pass None for object_id to create a new object."""
        request_body = {
            "object": {"id": object_id, "type": object_type},
            "fields": new_field_values,
        }
        if object_id is None:
            # If you have no object id because you're creating a new object, you need to format it slightly differently
            request_body = {"type": object_type, "fields": new_field_values}
        responses = self._send_and_validate_request(
            "/obj/upload", {"requests": [request_body]}, "responses", method="PUT"
        )

        if len(responses) != 1:
            raise ConstellationInvalidResponseException(
                "Expected exactly 1 response from /obj/upload", responses
            )

        return responses[0]

    # Getting history of changes to an object
    def object_log(
        self,
        object_ids=None,
        types=None,
        start_date=None,
        end_date=None,
        max_results=1000,
    ):
        """Find changes on the supplied types after the supplied start_date"""
        payload = {
            "limit": max_results,
            "order": "dsc",
        }
        if object_ids is not None:
            payload["object"] = [{"id": x} for x in object_ids]
        if types is not None:
            payload["Types"] = types
        if start_date is not None:
            payload["startDate"] = start_date
        if end_date is not None:
            payload["endDate"] = end_date
        return self._send_and_validate_request(
            "/obj/objectlog",
            payload,
        )

    # Getting type information
    def get_type(self, type_name):
        """Retrieve all of the fields and their formats for a given type"""
        return self._send_and_validate_request(
            "/obj/type/{}".format(type_name),
            {},
            method="GET",
        )

    # Internal helper functions
    def _auth_header_from_token(self, auth_token):
        """Build a authorization header when an auth token is supplied"""
        return {"Authorization": "Bearer " + str(auth_token)}

    def _send_and_validate_request(
        self,
        path,
        data,
        field_to_retrieve=None,
        method="POST",
        requires_auth_token=True,
    ):
        """Send a request and validate a request to the given path"""
        if requires_auth_token and not self._auth_token:
            raise ConstellationNotLoggedInException()

        url = self._host + path
        headers = {"Content-type": "application/json"}
        if self._auth_token:
            headers.update(self._auth_header_from_token(self._auth_token))
        if method == "POST":
            response = requests.post(
                url=url,
                data=json.dumps(data),
                headers=headers,
            )
        elif method == "PUT":
            response = requests.put(
                url=url,
                data=json.dumps(data),
                headers=headers,
            )
        elif method == "GET":
            response = requests.get(url=url, headers=headers)
        else:
            raise ConstellationInvalidMethodException(method, path)

        if response.status_code != HTTPStatus.OK:
            raise ConstellationException(
                "Unexpected non-200 response from constellation endpoint {}: {}".format(
                    url, response.text
                ),
                response.status_code,
            )

        if field_to_retrieve:
            field_value = response.json().get(field_to_retrieve)
            if not field_value:
                raise ConstellationInvalidResponseException(
                    "Could not retrieve field {} from request to {}".format(
                        field_to_retrieve, path
                    ),
                    response.text,
                )
            return field_value

        return response.json()

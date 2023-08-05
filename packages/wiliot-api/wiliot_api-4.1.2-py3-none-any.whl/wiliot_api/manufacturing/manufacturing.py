"""
Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import os.path
from wiliot_api.api_client import Client, WiliotCloudError
import datetime
from uuid import uuid4
import jwt


class ManufacturingClient(Client):
    def __init__(self, oauth_username=None, oauth_password=None, api_key=None, env='', log_file=None, logger_=None):
        self.client_path = "manufacturing/"
        super().__init__(oauth_username=oauth_username,
                         oauth_password=oauth_password, api_key=api_key, env=env, log_file=log_file, logger_=logger_)
    
    # Pixel Ownership Change functions
    
    def change_pixel_owner_by_range(self, from_owner_id, to_owner_id, from_pixel_id, to_pixel_id):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param from_pixel_id: String - The first pixel ID
        :param to_pixel_id: String - The last pixel ID
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        payload = {
            "fromTo": {
                "from": from_pixel_id,
                "to": to_pixel_id
            }
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e
    
    def change_pixel_owner_by_list(self, from_owner_id, to_owner_id, pixel_id_list):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_list: List of pixel IDs
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        assert isinstance(pixel_id_list, list), "pixel_id_list must be a list"
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        payload = {
            "tagIds": pixel_id_list
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e
    
    def change_pixel_owner_by_file(self, from_owner_id, to_owner_id, pixel_id_file_path):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_file_path : full path to a csv file containing one column called tagId
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        with open(pixel_id_file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(pixel_id_file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send, params=parameters)
                return res.get("trackingRequestId", None)
            except WiliotCloudError as e:
                print("Failed to request pixel ownership change")
                raise e
    
    def get_pixel_change_request_status(self, request_tracking_id):
        """
        Get information about the status of an ownership change request
        :param request_tracking_id: String - The request tracking ID returned from the change pixel owner request call
        :return: A dictionary with information about the details and the progress of the request
        """
        path = "ownerChange"
        res = self._get(path, {'requestId': request_tracking_id})
        return res
    
    def get_pixel_change_request_details(self, request_tracking_id, out_file):
        """
        Get detailed information about each of the pixels change of ownership was requested for
        :param request_tracking_id: String - The request tracking ID returned from the change pixel owner request call
        :param out_file: A file handle - to write the returned values to
        :return: A CSV file with a line per tag
        """
        path = "ownerChange/tagsInfo"
        params = {
            'requestId': request_tracking_id
        }
        res = self._get_file(path, out_file, params=params)
        return res
    
    def get_pixel_change_requests(self, owner_id):
        """
        Get a list of owner change requests made historically
        :return:
        """
        path = "ownerChange/requestsList"
        params = {
            'ownerId': owner_id,
            'cursor': None
        }
        has_next = True
        items = []
        while has_next:
            res = self._get(path, params=params)
            items = items + res['items']
            has_next = res['meta']['hasNext']
            params['cursor'] = res['meta']['cursor']
        return items

    def resolve_payload(self, payload, owner_id):
        """
        Resolve a tag's payload
        :param payload: valid Wiliot tag payload starting with the manufacturer ID
        :param owner_id: String - The ID of the owner to resolve this payload for
        :return: A dictionary from the returned JSON
        """
        now_ts = int(datetime.datetime.now().timestamp())
        decoded_token = jwt.decode(self.auth_obj.token['access_token'], options={"verify_signature": False})
        # Make sure the roles included in the token include "manufacturing"
        if "manufacturing" not in decoded_token['roles'] and "resolve" not in decoded_token['roles']:
            raise Exception("The provided API key is not a manufacturing API key. Please use the appropriate key")
        # Make sure that the generated token allows access to the requested owner
        if owner_id not in decoded_token['owners'].keys() and owner_id != 'wiliot_cloud-ops':
            raise Exception(f"The provided API key does not belong to the requested owner ID: {owner_id}")
        payload = {
            'timestamp': now_ts,
            'packets': [
                {
                    'timestamp': now_ts,
                    'payload': payload
                }
            ],
            'gatewayType': 'cli',
            'gatewayId': str(uuid4())
        }
        res = self._post("resolve", payload, override_client_path=f"owner/{owner_id}/")
        return res['data'][0]

    def safe_resolve_payload(self, payload, owner_id, verbose=False):
        """
        resolve payload with exception handling
        :param payload: valid Wiliot tag payload starting with the manufacturer ID
        :param owner_id: String - The ID of the owner to resolve this payload for
        :param verbose: bool - if true the resolve payload exception are printed, otherwise - are ignored
        :return: A dictionary from the returned JSON
        """
        try:
            data = self.resolve_payload(payload=payload, owner_id=owner_id)
        except Exception as e:
            if verbose:
                print(e)
            return {'externalId': 'no_external_id'}
        return data

    # Serialization API calls

    def serialize_tags(self, owner_id, tags_payload_file_path):
        """
        Request to serialize (set tag ID) for tag(s) by payload
        :param owner_id: String - the ID of the tags' owner
        :param tags_payload_file_path : full path to a csv file containing two columns:
            payload
            tagId
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        path = "serialization"
        parameters = {
            "owner": owner_id,
        }
        with open(tags_payload_file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(tags_payload_file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send, params=parameters)
                return res.get("trackingRequestId", None)
            except WiliotCloudError as e:
                print("Failed to request pixel ownership change")
                raise e

    def get_tags_serialization_request_details(self, request_tracking_id):
        """
        Get information about the status of a tag serialization request
        :param request_tracking_id: String - The request tracking ID returned from the serialize_tags call
        :return: A dictionary with information about the details and the progress of the request
        """
        path = "serialization"
        res = self._get(path, params={'requestId': request_tracking_id})
        return res

    def get_tags_serialization_request_info(self, request_tracking_id, out_file):
        """
        Get details about a tags serialization request
        :param request_tracking_id: String - The request tracking ID returned from the serialize_tags call
        :param out_file: A file handle - to write the returned values to
        :return: A CSV file with a line per tag
        """
        path = "serialization/tagsInfo"
        params = {
            'requestId': request_tracking_id
        }
        res = self._get_file(path, out_file, params=params)
        return res

    def get_tags_serialization_requests(self, owner_id):
        """
        Get a list of tag serialization requests made historically
        :return:
        """
        path = "serialization/requestsList"
        params = {
            'ownerId': owner_id,
            'cursor': None
        }
        has_next = True
        items = []
        while has_next:
            res = self._get(path, params=params)
            items = items + res['items']
            has_next = res['meta']['hasNext']
            params['cursor'] = res['meta']['cursor']
        return items

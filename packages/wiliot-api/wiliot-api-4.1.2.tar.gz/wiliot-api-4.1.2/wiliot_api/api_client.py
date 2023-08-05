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
import requests
from wiliot_api.security import security
import json
import logging
import urllib.parse

log_level = logging.INFO


class WiliotCloudError(Exception):
    pass


class Client:
    def __init__(self, oauth_username=None, oauth_password=None, api_key=None,
                 env='', api_version='v1', log_file=None, logger_=None):
        # The caller must provide either a set of oauth username abd password or an API key
        if api_key is None and (oauth_password is None or oauth_username is None):
            raise Exception('Provide either an API key or a username and password')
        
        self.env = env + "/" if env != '' and env != 'prod' else ''
        self.api_version = api_version
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        self.auth_obj = security.WiliotAuthentication(base_path=f"https://api.wiliot.com/{self.env}{self.api_version}/",
                                                      oauth_username=oauth_username,
                                                      oauth_password=oauth_password,
                                                      api_key=api_key)
        self.headers["Authorization"] = self.auth_obj.get_token()
        if logger_ is None:
            self.logger = logging.getLogger()
            self.logger.setLevel(log_level)
        else:
            self.logger = logging.getLogger(logger_)
        
        if not self.logger.hasHandlers():
            if log_file is not None:
                self.handler = logging.FileHandler(log_file)
            else:
                self.handler = logging.StreamHandler()
            self.handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)

    def _get_base_url(self, override_client_path=None, override_api_version=None):
        api_path = f"https://api.wiliot.com/{self.env}{self.api_version if override_api_version is None else override_api_version}/"
        base_url = api_path + self.client_path if override_client_path is None else api_path + override_client_path
        return base_url

    def _renew_token(self):
        if self.auth_obj.token_expired():
            self.headers["Authorization"] = self.auth_obj.get_token()
    
    def _get(self, path, params=None, override_client_path=None, override_api_version=None):
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        response = requests.get(base_path_to_use + path, headers=self.headers, params=params)
        try:
            message = response.json()
        except:
            message = response.text
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message
    
    def _get_file(self, path, out_file, params=None, override_client_path=None, override_api_version=None):
        """
        A version of _get which expects to get back a text/csv and requires the user to provide a file
        pointer to write the content to
        """
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        response = requests.get(base_path_to_use + path, headers=self.headers, params=params)
        out_file.write(response.text)
        if response.status_code != 200:
            raise WiliotCloudError(response.text)
        return response.ok
    
    def _put(self, path, payload, override_client_path=None, override_api_version=None):
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        response = requests.put(base_path_to_use + urllib.parse.quote(path), headers=self.headers,
                                data=json.dumps(payload))
        try:
            message = response.json()
        except:
            message = response.text
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message
    
    def _post(self, path, payload, params=None, files=None, override_client_path=None, override_api_version=None):
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        response = requests.post(base_path_to_use + urllib.parse.quote(path), headers=self.headers,
                                 data=json.dumps(payload) if payload is not None else None,
                                 params=params)
        try:
            message = response.json()
        except:
            message = response.text
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message
    
    def _post_with_files(self, path, files, payload=None, params=None, override_client_path=None, override_api_version=None):
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        if payload is None:
            payload = {}
        headers = self.headers.copy()
        headers.pop('Content-Type', None)
        response = requests.request("POST", base_path_to_use + urllib.parse.quote(path), headers=headers,
                                    data=payload,
                                    params=params,
                                    files=files)
        try:
            message = response.json()
        except:
            message = response.text
        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})
        if response.status_code != 200:
            raise WiliotCloudError(message)
        return message
    
    def _delete(self, path, payload=None, override_client_path=None, override_api_version=None):
        self._renew_token()
        base_path_to_use = self._get_base_url(override_client_path=override_client_path,
                                              override_api_version=override_api_version)
        response = requests.delete(base_path_to_use + urllib.parse.quote(path), headers=self.headers,
                                   data=json.dumps(payload) if payload is not None else None)
        if response.status_code != 200:
            raise WiliotCloudError(response.text)
        try:
            message = response.json()
        except:
            message = response.text
        return message

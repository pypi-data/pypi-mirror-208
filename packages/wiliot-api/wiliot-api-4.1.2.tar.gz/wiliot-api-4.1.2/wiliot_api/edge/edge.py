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
from wiliot_api.api_client import Client, WiliotCloudError
from enum import Enum


class GatewayNotFound(Exception):
    pass


class UnknownGatewayConfKey(Exception):
    pass


class BridgeAction(Enum):
    BLINK_LED = 'blinkBridgeLed'
    REBOOT = 'rebootBridge'


class EdgeClient(Client):
    def __init__(self, api_key, owner_id, env='', log_file=None, logger_=None):
        self.client_path = f"owner/{owner_id}/".format(owner_id=owner_id)
        self.owner_id = owner_id
        super().__init__(api_key=api_key, env=env, log_file=log_file, logger_=logger_)

    def get_gateways(self):
        """
        Get a list of gateways owned by the owner
        :return: A list of gateways
        """
        path = "gateway"
        response = self._get(path)
        res = response.get("data", [])
        return res

    def get_gateway(self, gateway_id):
        """
        Get a gateway's details including the applications it's associated with
        :param gateway_id:
        :return: A dictionary containing the information returned by the API
        """
        path = "gateway/{}".format(gateway_id)
        result = self._get(path)
        try:
            return result["data"]
        except KeyError:
            raise GatewayNotFound

    def register_gateway(self, gateways):
        """
        Register one or more Wiliot gateways
        :param gateways: list of gateway IDs to register
        :return: True if successful
        """
        assert isinstance(gateways, list), "gateways parameter must be a list of gateway IDs"
        payload = {
            "gateways": gateways
        }
        path = "gateway"
        response = self._put(path=path, payload=payload)
        return response["data"].lower() == "ok"

    def approve_gateway(self, gateway_id):
        """
        Approve a gateway. This endpoint must be called before a gateway can start pushing
        Wiliot packet payloads to the Wiliot cloud
        :param gateway_id: The ID of the gateway to approve
        the API will return a userCode only gateways in a 'registered' state
        :return: True if successful
        """
        path = "gateway/{}/approve".format(gateway_id)
        payload = {}
        response = self._post(path, payload)
        return response["data"].lower() == "ok"

    def delete_gateway(self, gateway_id):
        """
        Delete a gateway from the Wiliot cloud. This gateway will no longer be able to push Wiliot packet
        payloads to the Wiliot cloud
        :param gateway_id: The Id of the gateway to delete
        :return: True if successful
        """
        path = "gateway/{}".format(gateway_id)
        response = self._delete(path, payload={})
        return response['message'].lower().find("success") != -1

    def update_gateways_configuration(self, gateways, config):
        """
        Update one or more gateways' configuration
        :param gateways: A list of gateway IDs
        :param config: A dictionary - The desired configuration
        :return: True if successful
        """
        assert isinstance(gateways, list), "gateways argument must be a list"
        payload = {
            "desired": config,
            "gateways": gateways
        }

        path = "gateway"
        response = self._post(path=path, payload=payload)
        return response.get('message').lower().find('ok') != -1

    def register_third_party_gateway(self, gateway_id, gateway_type, gateway_name):
        """
        Register a third-party (non-Wiliot) gateway and receive an access and refresh token
        to be used by the gateway for sending tag payloads to the Wiliot cloud
        :param gateway_id: String - A unique ID for the gateway
        :param gateway_type: String - Can be used to group gateways of the same type
        :param gateway_name: String - A human readable name for the gateway
        :return: A dictionary of the following format:
        {
            "data": {
                "access_token": "...",
                "expires_in": 43199,
                "refresh_token": "...",
                "token_type": "Bearer",
                "userId": "...",
                "ownerId": "wiliot_cloud"
            }
        }
        """
        path = "gateway/{}/mobile".format(gateway_id)
        payload = {
            "gatewayType": gateway_type,
            "gatewayName": gateway_name
        }
        response = self._post(path, payload=payload)
        return response

    # Bridge related functionality
    def get_bridges_connected_to_gateway(self, gateway):
        """
        Get a list of gateways connected (controlled by) a gateway
        :param gateway: String - A Gateway ID to query for
        :return: A list of dictionaries for all bridges
        """
        path = "gateway/{}/bridge".format(gateway)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            if e.args[0]['message'].lower().find("not found") != -1:
                raise WiliotCloudError("Gateway {} could not be found".format(gateway))
            else:
                raise

    def get_bridges(self, online=None, gateway_id=None):
        """
        Get all bridges "seen" by gateways owned by the owner
        :param online: A boolean - optional. Allows to filter only online (True) or offline (False) bridges
        :param gateway_id: A string - optional. Allows to filer only bridges currently connected to the gateway
        :return: A list of bridges
        """
        path = "bridge"
        params = {}
        if online is not None:
            params['online'] = online
        try:
            res = self._get(path, params=params)
            bridges = res["data"]
            if gateway_id is not None:
                bridges = [b for b in bridges if any([c["connected"] and c["gatewayId"] == gateway_id for c
                                                      in b["connections"]])]
            return bridges
        except WiliotCloudError:
            raise

    def get_bridge(self, bridge_id):
        """
        Get information about a specific bridge
        :param bridge_id: String - the ID of the bridge to get information about
        :return: A dictionary containing bridge information
        :raises: WiliotCloudError if bridge cannot be found
        """
        path = "bridge/{}".format(bridge_id)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            raise

    def claim_bridge(self, bridge_id):
        """
        Claim bridge ownership
        :param bridge_id: String - The ID of the bridge to claim
        :return: True if successful
        """
        path = "bridge/{}/claim".format(bridge_id)
        try:
            res = self._post(path, None)
            return res["message"].lower().find("successfully") != -1
        except WiliotCloudError as e:
            print("Failed to claim bridge")
            raise WiliotCloudError("Failed to claim bridge. Received the following error: {}".format(e.args[0]))

    def unclaim_bridge(self, bridge_id):
        """
        Release ownership of claimed bridge
        :param bridge_id: String - The ID of the bridge to release
        :return: True if successful
        """
        path = "bridge/{}/unclaim".format(bridge_id)
        try:
            res = self._post(path, None)
            return res["message"].lower().find("successfully") != -1
        except WiliotCloudError as e:
            print("Failed to release bridge")
            raise WiliotCloudError(
                "Failed to release claimed bridge. Received the following error: {}".format(e.args[0]))

    def update_bridge_configuration(self, bridge_id, config={}, name=None):
        """
        Update a bridge's configuration
        :param bridge_id: A string - The ID of the bridge being updated
        :param config: Optional A dictionary of configuration keys and values
        :param name: Optional String - Specified the name for the bridge
        :return: True if the configuration update was received successfully. Note, that this is not an indication
        that a bridge's configuration was updated. To verify that configuration has been updated read the bridge
        configuration and compare to the requested values
        """
        path = "bridge/{}".format(bridge_id)
        payload = {
            "config": config
        }
        if name is not None:
            payload["name"] = name
        try:
            res = self._put(path, payload)
            return res["message"].lower().find("updated bridge success") != -1
        except WiliotCloudError as e:
            print("Failed to update bridge configuration")
            raise WiliotCloudError(
                "Failed to update bridge configuration. Received the following error: {}".format(e.args[0]))

    def send_action_to_bridge(self, bridge_id, action):
        """
        Send an action to a bridge
        :param bridge_id: String - the ID of the bridge to send the action to
        :param action: BridgeAction
        :return: True if the cloud successfully sent the action to the bridge, False otherwise
        """
        assert isinstance(action, BridgeAction), "action argument must be of type BridgeAction"
        path = "bridge/{}/action".format(bridge_id)
        payload = {
            "action": action.value
        }
        try:
            res = self._post(path, payload)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to send action to bridge")
            raise WiliotCloudError(
                "Failed to send action to bridge. Recevied the following error: {}".format(e.args[0]))

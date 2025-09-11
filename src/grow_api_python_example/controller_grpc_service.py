import logging
from typing import List, Optional

from betterproto.lib.google.protobuf import Empty
from grpc import StatusCode
from grpclib.client import Channel

import grow_api_python_example as growproto


class ControllerGrpcService():
    def __init__(self, stub: growproto.PsControllerServiceStub, host: str, port: int):
        self.stub = stub
        self.host = host
        self.port = port

    @classmethod
    def from_host(cls, host: str, port: int) -> Optional["ControllerGrpcService"]:
        try:
            channel = Channel(host=host, port=port)
            stub = growproto.PsControllerServiceStub(channel)
            return cls(stub, host, port)
        except Exception as e:
            logging.error(f"Error connecting to {host}:{port}, {e}")
            return None

    async def get_controller_info(self) -> Optional[growproto.GetControllerInfoResponse]:
        try:
            return await self.stub.get_controller_info(Empty())
        except Exception as e:
            logging.error(f"Error getting controller info from {self.host}:{self.port}, {e}")
            return None

    async def set_light_output(self, device_uids: List[str], red: float, far_red: float, blue: float, white: float) -> bool:
        """ Set the light output for the specified device UIDs. 0-100% for each channel.

        Returns:
            bool: True if the light output was set successfully, False otherwise.
        """
        try:
            request = growproto.SetLightOutputRequest(device_uids=device_uids, outputs= growproto.ChannelOutputsMessage(channel_names=["red","far red","blue","white"], outputs=[red, far_red, blue, white]))
            response: growproto.Status = await self.stub.set_light_output(request)
            return response.code == StatusCode.OK.value[0]
        except Exception as e:
            logging.error(f"Error setting light output on {self.host}:{self.port}, {e}")
            return False

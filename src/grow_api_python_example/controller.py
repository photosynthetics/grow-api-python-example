

import logging
from typing import Optional, Tuple

from betterproto.lib.google.protobuf import Empty
from grpclib.client import Channel

import grow_api_python_example as growproto
from grow_api_python_example.controller_grpc_service import \
    ControllerGrpcService
from grow_api_python_example.ip_util import (get_current_subnet,
                                             get_ip_addresses_on_same_subnet,
                                             is_socket_open_multiple)


async def connect_to_first_controller_on_network(interface: str, port: int) -> Optional[ControllerGrpcService]:
    subnet = get_current_subnet(interface)
    if subnet == "":
        logging.error(f"Could not determine subnet for interface {interface}. Confirm that you entered the correct interface name. E.g Wi-Fi on windows")
        return None
    all_ip_addresses = get_ip_addresses_on_same_subnet(subnet)
    open_ips = is_socket_open_multiple(all_ip_addresses, port, timeout=0.20)
    if not open_ips:
        logging.info("No open gRPC service found on the subnet.")
        return None
    for ip in open_ips:
        controller_service, controller_info = await connect_to_controller(ip, port)
        if controller_service is not None and controller_info is not None:
            return controller_service
    logging.info(f"Could not connect to any controller on the subnet {subnet} on interface {interface}")
    return None


async def connect_to_controller(host: str, port: int) -> Tuple[Optional[ControllerGrpcService], Optional[growproto.GetControllerInfoResponse]]:
    try:
        channel = Channel(host=host, port=port)
        stub = growproto.PsControllerServiceStub(channel)
        controller_info_response: growproto.GetControllerInfoResponse = await stub.get_controller_info(Empty())
        controller_service = ControllerGrpcService(stub, host, port)
        return controller_service, controller_info_response
    except Exception as e:
        logging.error(f"Error connecting to controller at {host}:{port}, {e}")
        if 'channel' in locals():  # Check if 'channel' was successfully created
            channel.close()
        return None, None


def pretty_print_controller_info(message: growproto.GetControllerInfoResponse):
    logging.info(f"Controller ID: {message.id}")
    logging.info(f"Sw version: {message.sw_version}")
    for idx, inteface in enumerate(message.interfaces):
        logging.info(f"Interface {idx}: id: {inteface.id}, submodules: {len(inteface.interface_submodules)}")
        for sub_idx, submodule in enumerate(inteface.interface_submodules):
            lights = [d for d in submodule.grow_rdm_devices if d.device_type == growproto.GrowDeviceType.grow_light_v1]
            logging.info(f"  Submodule {sub_idx}: id: {submodule.serial_number}, light count: {len(lights)}")
            for light_idx, light in enumerate(lights):
                logging.info(f"    Light {light_idx}: Bus id(rdm id): {light.device_uid}, type: {light.device_type}, fw version: {light.version}")
                logging.info(f"      Emitter temperature: {light.grow_light_state_message.emitter_temperature_c}C, Power draw: {light.grow_light_state_message.power_draw}W, Voltage: {light.grow_light_state_message.voltage}V, Current: {light.grow_light_state_message.current}A")


def get_light_uids_from_controller_info(message: growproto.GetControllerInfoResponse) -> list[str]:
    uids = []
    for inteface in message.interfaces:
        for submodule in inteface.interface_submodules:
            for light in submodule.grow_rdm_devices:
                uids.append(light.device_uid)
    return uids



# @dataclass(eq=False, repr=False)
# class InterfaceModuleMessage(betterproto.Message):
#     status: "Status" = betterproto.message_field(1)
#     id: str = betterproto.string_field(2)
#     sw_version: "VersionMessage" = betterproto.message_field(3)
#     interface_submodules: List["InterfaceSubmoduleMessage"] = betterproto.message_field(
#         4
#     )
#     session_id: int = betterproto.int32_field(5)
#     uptime: timedelta = betterproto.message_field(6)
#     is_updating_rdm_box_fw: bool = betterproto.bool_field(7)
#     settings: "InterfaceModuleSettings" = betterproto.message_field(8)
#     grpc_host: str = betterproto.string_field(9)
#     grpc_port: int = betterproto.int32_field(10)
#     submodule_fw_version: "VersionMessage" = betterproto.message_field(11)
#     git_status: "GitStatusMessage" = betterproto.message_field(12)
#     app_updates: List["GitHubReleaseMessage"] = betterproto.message_field(13)

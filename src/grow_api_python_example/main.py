
import datetime
import logging
import traceback
from grow_api_python_example.controller import pretty_print_controller_info, connect_to_first_controller_on_network, get_light_uids_from_controller_info

import asyncio


async def main():
    logging.basicConfig(level=logging.INFO)
    # Enter the interface name here. E.g "Wi-Fi" on windows, "eth0", "wlan0" on linux
    # The controller service broadcasts on port 50057
    controller = await connect_to_first_controller_on_network(interface="Wi-Fi", port=50057)
    if controller is None:
        logging.info("No controller found on the specified interface.")
        return
    logging.info(f"Connected to controller at {controller.host}:{controller.port}")
    # Getting the controller data. This contains information about the controller, and all devices currently connected to it.
    # The controller only updates its data every 5 seconds ish. So bear that in mind if you are polling for changes.
    # Inspect pretty_print_controller_info  function to get an idea of what information is available.
    controller_info = await controller.get_controller_info()
    if controller_info is None:
        logging.info("Failed to get controller info.")
        return
    pretty_print_controller_info(controller_info)
    uids = get_light_uids_from_controller_info(controller_info)
    logging.info(f"Found {len(uids)} lights: {uids}")
    logging.info("Setting all lights to 15% red and 15% blue for 6 seconds")
    did_set_light = await controller.set_light_output(uids, red=15, far_red=0, blue=15, white=0)
    if did_set_light:
        logging.info("Successfully set light output.")
    else:
        logging.info("Failed to set light output.")

    
    logging.info("Waiting 6 seconds to let the controller update data, reading info, and then turning off lights\n")
    await asyncio.sleep(6)

    controller_info = await controller.get_controller_info()
    if controller_info is None:
        logging.info("Failed to get controller info.")
        return
    pretty_print_controller_info(controller_info)
    did_set_light = await controller.set_light_output(uids, red=0, far_red=0, blue=0, white=0)
    if did_set_light:
        logging.info("Successfully set light output.")
    else:
        logging.info("Failed to set light output.")

if __name__ == "__main__":
    try:
        asyncio.run(main())  # python 3.7 only
        input("Press any key to exit")
    except Exception as e:
        print(e)
        traceback.print_exc()
        input("Press any key to exit")

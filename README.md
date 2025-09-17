# grow-api-python-example

## Setup
Preferably use python >= 3.10. (This has only been tested with python 3.12 on windows so far).

    python3 -m venv .venv

Activate the virtual environment:

    source .venv/bin/activate  # Linux/MacOS
    .venv\Scripts\Activate.ps1     # Windows

Install the example. Include the last dot (.)

    pip install -e .


## Generating gRPC code from proto files

The proto files are located in the `proto` directory. You can use the provided script to compile the proto files into python code.
This has already been done, and the generated code is located in the `__init__.py` file in the `src/grow_api_python_example` directory.

    python scripts/script_compile_proto_file.py

You can also look at the script to see what commands are being run to generate the code.


## Usage
(PS. The controller must be on the same network as your computer to use this example)

This example aims to demonstrate how to find the controller grpc service IP on the network,
fetch information about all devices connected to the controller, and how to send light output commands to a light device.




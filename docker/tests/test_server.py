import pytest
import sys
from server import Layer
from server import Server

HOST = "localhost"
PORT = 3333

def test_python_version():
  from packaging.version import Version
  
  target_version="3.10.0"
  max_version="3.14.0"
  
  current_version = sys.version.split()[0]
  assert Version(current_version) >= Version(target_version)
  assert Version(current_version) < Version(max_version)


def test_dependencies():
  import importlib
  
  try:
    importlib.import_module("pytest")
    importlib.import_module("packaging")
    importlib.import_module("importlib")
    importlib.import_module("sys")
    importlib.import_module("psutil")
        
    importlib.import_module("socket")
    importlib.import_module("json")
    importlib.import_module("client")
        
    dependencies_met = True
  except ModuleNotFoundError:
    dependencies_met = False
        
  assert dependencies_met


def test_resource_usage():
  import psutil
  
  threshold=80.0
  
  # Get CPU usage as percentage every second
  cpu_usage = psutil.cpu_percent(interval=1.0)
  
  # Get Memory usage info and percentage
  memory_info = psutil.virtual_memory()
  memory_usage = memory_info.percent
  
  print("\n---- Server resource usage test: ----")
  print("Current CPU usage: {}%".format(cpu_usage))
  print("Current RAM usage: {}%".format(memory_usage))
  print("-------------------------------------\n")
  
  assert cpu_usage <= threshold
  assert memory_usage <= threshold


def test_decapsulate():
  message = 'Pytest_Data_Value'
  packet = ['IP Header', ['TCP Header', [message]]]
  presumed_segment = ['TCP Header', [message]]
  presumed_data = [message]

  # Stored values on memory will change on each .pop(), so assert needs to be done on demand
  network = Layer(packet)
  segment = network.decapsulate(network.PDU)
  
  assert segment == presumed_segment
  
  transport = Layer(segment)
  data = transport.decapsulate(transport.PDU)
  
  assert data == presumed_data
  
  application = Layer(data)
  resultant_message = application.decapsulate(application.PDU)
  
  assert resultant_message == message


def test_setup(mocker):
  import socket
  
  # Patch the function call that creates a socket
  mock_socket = mocker.patch("socket.socket")
  mock_sock_instance = mock_socket.return_value
  
  server = Server(HOST, PORT)
  server.setup()
  
  hook = (HOST, PORT)
  mock_sock_instance.bind.assert_called_once_with(hook)
  
  max_connections = 1
  mock_sock_instance.listen.assert_called_once_with(max_connections)
  
  
def test_await_message(mocker):
  import json
  
  value_sent = 'ACK'
  received_value = json.dumps(value_sent).encode()
  
  server = Server(HOST, PORT)
  server.CONNECTION = mocker.MagicMock()
  
  # Patch the function call to simulate receiving our sent value
  mock_recv = mocker.patch.object(server.CONNECTION, "recv", return_value=received_value)
  
  server.await_message()
  
  assert server.MESSAGE == value_sent
  
  
def test_stack(mocker):
  import json
  
  # Pre-Run Block #
  sent_message = 'Pytest_Data_Value'
  received_frame = ['Frame Header', ['IP Header', ['TCP Header', [sent_message]]], 'Frame Footer']
  
  # Stored values on memory will change on each .pop(), so we'll check against what is removed:
  shed_network = ['IP Header']
  shed_transport = ['TCP Header']
  shed_application = []
  
  # Now mock the method to surveil for the object status (run module and surveil data)
  spy_decaps = mocker.spy(Layer, "decapsulate")
  
  # ~> Create the object with the spy mocker method and add received frame
  server = Server(HOST, PORT)
  server.MESSAGE = received_frame
  
  # ~> Run tested function with injected mocker
  server.stack()
  
  # Post-Run Block #
  # Assert ammount of surveiled calls
  assert spy_decaps.call_count == 4
  
  # Get list of what was called by surveiled function
  calls_list = spy_decaps.call_args_list
  
  # Identify what call represents each layer, and return arguments received
  net_interface_call = calls_list[0]
  network_call = calls_list[1]
  transport_call = calls_list[2]
  application_call = calls_list[3]
  
  # Identify what was processed as the PDUs for each layer
  remaining_network = network_call.args[1]
  remaining_transport = transport_call.args[1]
  remaining_application = application_call.args[1]
  
  # Assess values returned:
  assert remaining_network == shed_network
  assert remaining_transport == shed_transport
  assert remaining_application == shed_application
  

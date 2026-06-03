import pytest
import sys
from client import Layer
from client import Client

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
  
  print("\n---- Client resource usage test: ----")
  print("Current CPU usage: {}%".format(cpu_usage))
  print("Current RAM usage: {}%".format(memory_usage))
  print("-------------------------------------\n")
  
  assert cpu_usage <= threshold
  assert memory_usage <= threshold


def test_encapsulate():
  message = 'Pytest_Data_Value'
  
  application = Layer()
  transport = Layer()
  network = Layer()
  
  data = application.encapsulate(message, None)
  segment = transport.encapsulate(data, 'TCP')
  packet = network.encapsulate(segment, 'IP')
  
  presumed_application = [message]
  presumed_transport = ['TCP Header', [message]]
  presumed_network = ['IP Header', ['TCP Header', [message]]]
  
  assert presumed_application == data
  assert presumed_transport == segment
  assert presumed_network == packet


def test_setup(mocker):
  import socket
  
  mock_socket = mocker.MagicMock()
  
  # Patch the function call to connect to our mock socket
  mock_connection = mocker.patch("client.socket.create_connection", return_value=mock_socket)

  client = Client(HOST, PORT)
  client.setup()
  
  assert client.CONNECTION == mock_socket
  
  
def test_await_response(mocker):
  import json
  
  value_sent = 'ACK'
  received_value = json.dumps(value_sent).encode()
  
  client = Client(HOST, PORT)
  client.CONNECTION = mocker.MagicMock()
  
  # Patch the function call to simulate receiving our sent value
  mock_recv = mocker.patch.object(client.CONNECTION, "recv", return_value=received_value)
  
  client.await_response()
  
  assert client.MESSAGE == value_sent
  
  
def test_stack(mocker):
  import json
  
  # Pre-Run Block #
  # Input mocker values
  py_file_name = "client"
  input_value = 'Pytest_Data_Value'
  
  # Simulate user input by injecting and surveiling value when input is called in client.py
  input_wrapper = mocker.patch("{}.input".format(py_file_name), return_value=input_value)
  
  # Now mock the method to surveil for the object status (run module and surveil data)
  spy_encaps = mocker.spy(Layer, "encapsulate")
  
  # ~> Create the object with the spy mocker method
  client = Client(HOST, PORT)
  
  # Now that the object was created, inject a mocker directly into client.CONNECTION (skip socket bind)
  client.CONNECTION = mocker.MagicMock()
  
  # Inject mocker into function of the created object (skip function)
  mock_handshake = mocker.patch.object(client, "handshake")
  
  # Mock the JSON method to surveil inserted arguments (Only works on the injected object's methods)
  spy_json = mocker.spy(json, "dumps")
  
  # ~> Run tested function with injected input and mocks
  client.stack()
  
  # Post-Run Block #
  # Assert injected input and ammount of surveiled calls
  assert input_wrapper.return_value == input_value
  assert spy_encaps.call_count == 4
  
  # Get list of what was called by surveiled function
  calls_list = spy_encaps.call_args_list
  
  # Identify what call represents each layer, and return arguments received
  application_call = calls_list[0]
  transport_call = calls_list[1]
  network_call = calls_list[2]
  net_interface_call = calls_list[3]
  json_call = spy_json.call_args
  
  # Identify what was processed as the PDUs for each layer
  received_message = application_call.args[1]
  application_pdu = transport_call.args[1]
  transport_pdu = network_call.args[1]
  network_pdu = net_interface_call.args[1]
  net_interface_pdu = json_call.args[0]
  
  # Lay out the values that should be checked against:
  presumed_application = [input_value]
  presumed_transport = ['TCP Header', [input_value]]
  presumed_network = ['IP Header', ['TCP Header', [input_value]]]
  presumed_net_interface = ['Frame Header', ['IP Header', ['TCP Header', [input_value]]], 'Frame Footer']
  
  # Assess values returned:
  assert received_message == input_value
  assert application_pdu == presumed_application
  assert transport_pdu == presumed_transport
  assert network_pdu == presumed_network
  assert net_interface_pdu == presumed_net_interface
  
  # Get value sent by JSON with injected .dumps and assert if it was called correctly
  client.CONNECTION.sendall.assert_called_once_with(json.dumps(presumed_net_interface).encode())
  

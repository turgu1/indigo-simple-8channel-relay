# Robert's 8 Channel Relay Plugin for Indigo

This plugin is using HTTP protocol to access and direct an 8 Channel Relay board RELAY-NET-V5.8. It was built using David Nendhall plugin effort (see [here](https://github.com/davidnewhall/indigo-8channel-relay)). 

All sprinkler related code has been removed. A subprocess is used with `curl` to transmit commands to the board. As the documentation for the board is lacking for the other supported protocols (port 1234 and Modbus port 502), this was the only found way to make it works (Many trials are done with Modbus and older port 1234 protocols but nothing worked).

This plugin requires the use of the `subprocess32` python library. To install, you must first install the `pip` installation tool on your computer, than install the python library. The `subprocess32` implements the Python 3 subprocess added features in a Python 2 context.

## License

- [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)

# Simple 8 Channel Relay Plugin for Indigo

This plugin is using HTTP protocol to access and direct an 8 Channel Relay board RELAY-NET-V5.8 from IotZone. It was built as a spinoff of David Nendhall's plugin effort (see [here](https://github.com/davidnewhall/indigo-8channel-relay)). 

All sprinkler related code has been removed. A subprocess is used with `curl` to transmit commands to the board. As the documentation for the board is lacking for the other supported protocols (port 1234 and Modbus port 502), this was the only found way to make it works (Many trials are done with Modbus and older port 1234 protocols but nothing worked).

This plugin requires the use of the `subprocess32` python library. To install, you must first install the `pip` installation tool on your computer (as described [here](https://pip.pypa.io/en/stable/installing/)), then install the python library. The `subprocess32` implements the Python 3 subprocess added features in a Python 2 context. You can find the library information [here](https://pypi.org/project/subprocess32/).

Here are the commands to do in a terminal window on your computer. First to install pip if not already installed:

```bash
$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$ sudo python get-pip.py
```

Then to install the `subprocess32` library:

```bash
$ sudo pip install subprocess32
```

You can then install the indigo plugin, downloading the zip file from the releases page [here](https://github.com/turgu1/indigo-simple-8channel-relay/releases).

## License

- [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)


<img src="picture/relay-net-v5.8.jpg" alt="picture" width="800"/>

""" Robert's 8 Channel Relay Plugin for Indigo.
    First Release Date: December 16, 2020
    Author: Guy Turcotte
    License: GPLv2
"""

from datetime import datetime
import indigo
import subprocess
import json

class Plugin(indigo.PluginBase):
    """ Indigo Plugin """

    def __init__(self, pid, name, version, prefs):
        """ Initialize Plugin. """
        indigo.PluginBase.__init__(self, pid, name, version, prefs)
        self.debug = False

    def validateDeviceConfigUi(self, values, type_id, did):
        """ Validate the config for each sub device is ok. Set address prop. """
        errors = indigo.Dict()
        dev = indigo.devices[did]
        props = dev.pluginProps
        try:
            channel = int(values["channel"])
        except:
            channel = 0
        prefix = "r" if type_id == "Relay" else "i"
        values["address"] = u"{} {}{}".format(props.get("hostname", values["address"]), prefix, channel)
        dev.replacePluginPropsOnServer(props)
        return (True, values)


    def getDeviceFactoryUiValues(self, dev_id_list):
        """ Called when the device factory config UI is first opened.
        Used to populate the dialog with values from device 0. """
        values = indigo.Dict()
        errors = indigo.Dict()
        # Retrieve parameters stored in device 0"s props.
        if dev_id_list:
            dev = indigo.devices[dev_id_list[0]]
            values["address" ] = dev.pluginProps.get("hostname", u"192.168.1.166")
            values["port"    ] = dev.pluginProps.get("port",     80)
            values["username"] = dev.pluginProps.get("username", "admin")
            values["pwd"     ] = dev.pluginProps.get("pwd",      "12345678")
        return (values, errors)

    def closedDeviceFactoryUi(self, values, cancelled, dev_id_list):
        """ Save the DeviceFactory properties to each sub device. """
        if cancelled is True:
            if "createdDevices" in values and values["createdDevices"] != "":
                for did in values["createdDevices"].split(","):
                    indigo.device.delete(indigo.devices[int(did)])
                    dev_id_list.remove(int(did))
        else:
            if ("removedDevices" in values and values["removedDevices"] != ""):
                for did in values["removedDevices"].split(","):
                    dev = indigo.devices[int(did)]
                    indigo.device.delete(dev)
                    if did not in values["createdDevices"].split(","):
                        # do not log if the device was added/removed in one shot.
                        indigo.server.log(u"Deleted Device: {}".format(dev.name))
                    dev_id_list.remove(int(did))
        for did in dev_id_list:
            dev = indigo.devices[did]
            props = dev.pluginProps
            channel = props.get("channel", 0)
            prefix = "r" if dev.deviceTypeId == "Relay" else "i"
            props["hostname"] = values.get("address",  props.get("hostname", ""))
            props["port"    ] = values.get("port",     props.get("port", "1234"))
            props["username"] = values.get("username", props.get("username", "admin"))
            props["pwd"     ] = values.get("pwd",      props.get("pwd", "12345678"))
            props["address" ] = u"{} {}{}".format(props["hostname"], prefix, channel)
            dev.replacePluginPropsOnServer(props)
        self.set_device_states()
        return values

    def runConcurrentThread(self):
        """ Method called by Indigo to poll the relay board(s).
        This is required because the board has no way to send an update to Indigo.
        If the input sensors are tripped we have to poll to get that state change.
        """
        try:
            while True:
                self.set_device_states()
                self.sleep(int(indigo.activePlugin.pluginPrefs.get("interval", 15)))
        except self.StopThread:
            pass

    def actionControlUniversal(self, action, dev):
        """ Contral Misc. Actions here, like requesting a status update. """
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            self.set_device_states()

    def actionControlDevice(self, action, dev):
        """ Callback Method to Control a Relay Device. """
        channel = dev.pluginProps.get("channel", -1)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            try:
                self.send_cmd(dev.pluginProps, "relay.cgi?relayon"+channel+"=on")
            except KeyError:
                dev.setErrorStateOnServer(u"Relay Channel Missing! Configure Device Settings.")
            except Exception as err:
                dev.setErrorStateOnServer(u"Error turning on relay device: {}".format(err))
            else:
                dev.updateStateOnServer("onOffState", True)
                if dev.pluginProps.get("logActions", True):
                    indigo.server.log(u"Sent \"{}\" on".format(dev.name))
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            try:
                self.send_cmd(dev.pluginProps, "relay.cgi?relayoff"+channel+"=off")
            except KeyError:
                dev.setErrorStateOnServer(u"Relay Channel Missing! Configure Device Settings.")
            except Exception as err:
                dev.setErrorStateOnServer(u"Error turning off relay device: {}".format(err))
            else:
                dev.updateStateOnServer("onOffState", False)
                if dev.pluginProps.get("logActions", True):
                    indigo.server.log(u"Sent \"{}\" off".format(dev.name))
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            command, reply, state = ("relay.cgi?relayon"+channel+"=on", "on", True)
            if dev.states["onOffState"]:
                command, reply, state = ("relay.cgi?relayoff"+channel+"=off", "off", False)
            try:
                self.send_cmd(dev.pluginProps, command)
            except KeyError:
                dev.setErrorStateOnServer(u"Relay Channel Missing! Configure Device Settings.")
            except Exception as err:
                dev.setErrorStateOnServer("Error toggling relay device: {}".format(err))
            else:
                dev.updateStateOnServer("onOffState", state)
                if dev.pluginProps.get("logActions", True):
                    indigo.server.log(u"Sent \"{}\" {}".format(dev.name, reply))


    def _change_factory_device_type(self, values, dev_id_list):
        """ Devices.xml Callback Method to make sure changing the factory device type is safe. """
        rem_devs = values["removedDevices"].split(",")
        if rem_devs[0] == "":
            rem_devs = []
        values["deviceGroupList"] = [v for v in dev_id_list if v not in values["removedDevices"].split(",")]
        return values

    def _get_device_list(self, filter, values, dev_id_list):
        """ Devices.xml Callback Method to return all sub devices. """
        return_list = list()
        for did in dev_id_list:
            name = indigo.devices[did].name if did in indigo.devices else u"- device missing -"
            if str(did) not in values.get("removedDevices", "").split(","):
                return_list.append((did, name))
        return return_list

    def _add_sensor(self, values, dev_id_list):
        """ Devices.xml Callback Method to add a new Relay sub-device. """
        if len(dev_id_list)-len(values["removedDevices"].split(",")) >= 8:
            return values
        dev = indigo.device.create(indigo.kProtocol.Plugin, deviceTypeId="Sensor")
        dev.model = u"Robert's 8 Channel Relay Board"
        dev.subModel = u"Input"
        dev.replaceOnServer()
        values["createdDevices"] += ","+str(dev.id) if values["createdDevices"] != "" else str(dev.id)
        return values

    def _add_relay(self, values, dev_id_list):
        """ Devices.xml Callback Method to add a new Relay sub-device. """
        if len(dev_id_list)-len(values["removedDevices"].split(",")) >= 8:
            return values
        dev = indigo.device.create(indigo.kProtocol.Plugin, deviceTypeId="Relay")
        dev.model = u"Robert's 8 Channel Relay Board"
        dev.subModel = u"Relay"
        dev.replaceOnServer()
        values["createdDevices"] += ","+str(dev.id) if values["createdDevices"] != "" else str(dev.id)
        return values

    def _remove_devices(self, values, dev_id_list):
        """ Devices.xml Callback Method to remove devices. """
        for did in dev_id_list:
            if str(did) in values["deviceGroupList"]:
                dev = indigo.devices[did]
                values["removedDevices"] += ","+str(dev.id) if values["removedDevices"] else str(dev.id)
        return values

    def _pulse_relay(self, action, dev):
        """ Actions.xml Callback Method to pulse a relay. """
        channel = dev.pluginProps.get("channel", -1)
        try:
            self.send_cmd(dev.pluginProps, "relay.cgi?pulse"+channel+"=pulse")
        except KeyError:
            dev.setErrorStateOnServer(u"Relay Channel Missing! Configure Device Settings.")
        except Exception as err:
            dev.setErrorStateOnServer("Error Pulsing Relay: {}".format(err))
        else:
            if dev.pluginProps.get("logActions", True):
                indigo.server.log(u"Sent \"{}\" relay pulse".format(dev.name))
            dev.updateStateOnServer("pulseCount", dev.states.get("pulseCount", 0) + 1)
            dev.updateStateOnServer("pulseTimestamp", datetime.now().strftime("%s"))
            dev.updateStateOnServer("onOffState", False)  # Pulse always turns off.

    def _reset_pulse_count(self, action, dev):
        """ Set the pulse count for a device back to zero. """
        dev.updateStateOnServer("pulseCount", 0)

    def _reset_device_pulse_count(self, values, type_id, did):
        """ Set the pulse count for a device back to zero. """
        indigo.devices[did].updateStateOnServer("pulseCount", 0)

    @staticmethod
    def set_device_states():
        """ Updates Indigo with current devices" states. """
        devs      = list()
        hosts     = list()
        # Build two lists: host/port combos, and (sub)devices.
        for dev in indigo.devices.iter("self"):
            if (dev.enabled and dev.configured 
                    and "hostname" in dev.pluginProps
                    and "port"     in dev.pluginProps
                    and "username" in dev.pluginProps
                    and "pwd"      in dev.pluginProps):
                # Make a list of the plugin"s devices and a set of their hostnames.
                hosts.append((dev.pluginProps["hostname"], 
                              dev.pluginProps["port"    ],
                              dev.pluginProps["username"],
                              dev.pluginProps["pwd"     ]))
                devs.append(dev)

        # Loop each unique host/port combo and poll it for status, then update its devices.
        for host, port, username, pwd in set(hosts):
            try:
                json_data = Plugin.send_cmd(dev.pluginProps, "state.cgi")
                json_info = json.loads(json_data)
            except Exception as err:
                dev.setErrorStateOnServer("Error Reading state: {}".format(err))
                return

            # Update all the devices that belong to this hostname/port.

            inputs  = json_info['input' ]
            outputs = json_info['output']

            for dev in devs:
                chan = dev.pluginProps.get("channel", -1)
                if (dev.pluginProps["hostname"], dev.pluginProps["port"]) != (host, port):
                    # Device does not match, carry on.
                    continue
                if dev.deviceTypeId == "Relay":
                    state = True if outputs[int(chan)-1] == "1" else False
                elif dev.deviceTypeId == "Sensor":
                    state = True if inputs[int(chan)-1] == "1" else False
                if dev.pluginProps.get("logChanges", True):
                    if dev.states["onOffState"] != state:
                        reply = "on" if state else "off"
                        indigo.server.log(u"Device \"{}\" turned {}"
                                          .format(dev.name, reply))
                dev.updateStateOnServer("onOffState", state)
                continue

    @staticmethod
    def send_cmd(values, cmd):
        """ Sends a simple command to the relay board. """
        timeout_duration = indigo.activePlugin.pluginPrefs.get("timeout", 4)
        try:
            the_cmd = "curl -G --connect-timeout {} --user {}:{} http://{}:{}/{}".format(
                  timeout_duration,
                  values["username"], 
                  values["pwd"], 
                  values["hostname"], 
                  values["port"], 
                  cmd)
            #indigo.server.log(u"Relay shell cmd: {}".format(the_cmd))
            proc = subprocess.Popen(the_cmd,
              stdout=subprocess.PIPE,
              shell=True)
            result, err = proc.communicate()
            # indigo.server.log(u"Relay shell result: {}".format(result))
            # if err != None:
            #   indigo.server.log(u"Relay Shell launch error: {}".format(err))
            return result
        except Exception as err:
            indigo.server.log(u"Relay Communication Error: {} ({}:{}/{})"
                              .format(err, values["hostname"], values["port"], timeout_duration))
            raise
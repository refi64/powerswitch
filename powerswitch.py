#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import sys


class PowerSwitch:
    DEVICE_TYPE_LINE_POWER = 1

    def __init__(self):
        self.bus = dbus.SystemBus(mainloop=DBusGMainLoop())

        self.bus.add_signal_receiver(self.on_device_properties_changed,
                                     'PropertiesChanged',
                                     'org.freedesktop.DBus.Properties',
                                     'org.freedesktop.UPower', None,
                                     arg0='org.freedesktop.UPower.Device')

        self.upower = self.bus.get_object('org.freedesktop.UPower',
                                          '/org/freedesktop/UPower')
        self.upower_control = dbus.Interface(self.upower, 'org.freedesktop.UPower')

        self.tuned = self.bus.get_object('com.redhat.tuned', '/Tuned')
        self.tuned_control = dbus.Interface(self.tuned, 'com.redhat.tuned.control')

    def get_device_property(self, device_object, prop):
        props = dbus.Interface(device_object, 'org.freedesktop.DBus.Properties')
        return props.Get('org.freedesktop.UPower.Device', prop)

    def on_device_properties_changed(self, iface, changed, invalidated):
        if 'Online' in changed:
            self.update_profile()

    def update_profile(self):
        devices = self.upower_control.EnumerateDevices()
        for device_path in devices:
            device = self.bus.get_object('org.freedesktop.UPower', device_path)

            if (self.get_device_property(device, 'Type')
                        == self.DEVICE_TYPE_LINE_POWER
                    and self.get_device_property(device, 'PowerSupply')):

                if self.get_device_property(device, 'Online'):
                    profile = 'throughput-performance'
                else:
                    profile = 'powersave'

                ret, message = self.tuned_control.switch_profile(profile)
                if not ret:
                    print(f'WARNING: failed to set profile to {profile}: {message}',
                          file=sys.stderr)
                else:
                    print(f'Set profile to {profile}')

                break


def main():
    powerswitch = PowerSwitch()
    powerswitch.update_profile()

    main_loop = GLib.MainLoop()
    main_loop.run()


if __name__ == '__main__':
    main()

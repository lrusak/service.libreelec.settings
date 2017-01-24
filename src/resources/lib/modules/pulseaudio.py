
# -*- coding: utf-8 -*-

import os
import xbmc
import time
import dbus
import dbus.service
import uuid
import xbmcgui
import threading
import oeWindows
import ConfigParser

from functools import partial

class pulseaudio:

    ENABLED = False
    PULSEAUDIO_DAEMON = None
    menu = {
        '6': {
            'name': 32393,
            'menuLoader': 'menu_connections',
            'listTyp': 'pulselist',
            'InfoText': 780,
            },
        }

    def __init__(self, oeMain):
        try:
            oeMain.dbg_log('pulseaudio::__init__', 'enter_function', 0)
            self.listItems = {}
            self.busy = 0
            self.oe = oeMain
            self.visible = False
            self.oe.dbg_log('pulseaudio::__init__', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::__init__', 'ERROR: (' + repr(e) + ')', 4)

    def clear_list(self):
        try:
            remove = [entry for entry in self.listItems]
            for entry in remove:
                self.listItems[entry] = None
                del self.listItems[entry]
        except Exception, e:
            self.oe.dbg_log('pulseaudio::clear_list', 'ERROR: (' + repr(e) + ')', 4)

    def do_init(self):
        try:
            self.oe.dbg_log('pulseaudio::do_init', 'enter_function', 0)
            self.visible = True
            self.oe.dbg_log('pulseaudio::do_init', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::do_init', 'ERROR: (' + repr(e) + ')', 4)

    def exit(self):
        try:
            self.oe.dbg_log('pulseaudio::exit', 'enter_function', 0)
            self.visible = False
            self.clear_list()
            self.oe.dbg_log('pulseaudio::exit', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::exit', 'ERROR: (' + repr(e) + ')', 4)

    def load_values(self):
        try:
            self.oe.dbg_log('pulseaudio::load_values', 'enter_function', 0)
            self.oe.dbg_log('pulseaudio::load_values', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::load_values', 'ERROR: (' + repr(e) + ')')

    def menu_connections(self, focusItem, services={}, removed={}, force=False):
        try:
            self.oe.dbg_log('pulseaudio::menu_connections', 'enter_function', 0)
            self.oe.set_busy(1)

            # type 1=int, 2=string, 3=array

            properties = {
                0: {
                    'flag': 0,
                    'type': 2,
                    'values': ['device.description'],
                    },
                1: {
                    'flag': 0,
                    'type': 2,
                    'values': ['device.icon_name'],
                    },
                2: {
                    'flag': 0,
                    'type': 3,
                    'values': ['Profiles'],
                    },
                3: {
                    'flag': 0,
                    'type': 2,
                    'values': ['ActiveProfile'],
                    },
                }
            
            address = 'unix:path=/var/run/pulse/dbus-socket'
            self.pulse_bus = dbus.connection.Connection(address)
            pulse_core = self.pulse_bus.get_object(object_path='/org/pulseaudio/core1')
            pulse_core_interface = dbus.Interface(pulse_core, dbus.PROPERTIES_IFACE)
            cards = pulse_core_interface.Get('org.PulseAudio.Core1', 'Cards')    

            rebuildList = 0
            dictProperties = {}
            
            if len(cards) != len(self.listItems) or force:
                rebuildList = 1
                self.oe.winOeMain.getControl(int(self.oe.listObject['pulselist'])).reset()
            else:
                for card in cards:
                    if card not in self.listItems:
                        rebuildList = 1
                        self.oe.winOeMain.getControl(int(self.oe.listObject['pulselist'])).reset()
                        break
            
            for card in cards:
                pulse_card = self.pulse_bus.get_object(object_path=card)
                pulse_card_interface = dbus.Interface(pulse_card, dbus.PROPERTIES_IFACE)
                dbusServiceProperties = pulse_card_interface.GetAll('org.PulseAudio.Core1.Card')

                propertyList = {}
                for props in dbusServiceProperties:
                    if props == 'PropertyList':
                        for item in dbusServiceProperties[props]:
                            propertyList[item] = "".join(chr(b) for b in dbusServiceProperties[props][item])

                dictProperties = {}
                if rebuildList == 1:
                    if 'device.description' in propertyList:
                        cardName = propertyList['device.description']
                    else:
                        cardName = dbusServiceProperties['Name']
                    if cardName != '':
                        dictProperties['entry'] = card
                        dictProperties['modul'] = self.__class__.__name__
                        dictProperties['action'] = 'open_context_menu'
                
                for prop in properties:
                    result = dict(dbusServiceProperties.items() + propertyList.items())
                    for value in properties[prop]['values']:
                        if value in result:
                            result = result[value]
                            properties[prop]['flag'] = 1
                        else:
                            properties[prop]['flag'] = 0
                        if properties[prop]['flag'] == 1:
                            if properties[prop]['type'] == 1:
                                result = unicode(int(result))
                            if properties[prop]['type'] == 2:
                                result = unicode(result)
                            if properties[prop]['type'] == 3:
                                result = unicode(len(result))
                            if rebuildList == 1:
                                dictProperties[value] = result
                            else:
                                if self.listItems[card] != None:
                                    self.listItems[card].setProperty(value, result)
                if rebuildList == 1:
                    self.listItems[card] = self.oe.winOeMain.addConfigItem(cardName, dictProperties, self.oe.listObject['pulselist'])
                else:
                    if self.listItems[card] != None:
                        self.listItems[card].setLabel(cardName)
                        for dictProperty in dictProperties:
                            self.listItems[card].setProperty(dictProperty, dictProperties[dictProperty])
            self.oe.set_busy(0)
            self.oe.dbg_log('pulseaudio::menu_connections', 'exit_function', 0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('pulseaudio::menu_connections', 'ERROR: (' + repr(e) + ')', 4)

    def open_context_menu(self, listItem):
        try:
            self.oe.dbg_log('pulseaudio::open_context_menu', 'enter_function', 0)
            values = {}
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['pulselist']).getSelectedItem()
            if listItem is None:
                self.oe.dbg_log('pulseaudio::open_context_menu', 'exit_function (listItem=None)', 0)
                return
            
            values[1] = {
                    'text': self.oe._(32394),
                    'action': 'set_default',
                    }
            if len(listItem.getProperty('Profiles')) > 0:
                values[2] = {
                    'text': self.oe._(32395),
                    'action': 'set_profile',
                    }
            
            items = []
            actions = []
            for key in values.keys():
                items.append(values[key]['text'])
                actions.append(values[key]['action'])
            select_window = xbmcgui.Dialog()
            title = self.oe._(32012).encode('utf-8')
            result = select_window.select(title, items)
            if result >= 0:
                getattr(self, actions[result])(listItem)
            self.oe.dbg_log('pulseaudio::open_context_menu', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::open_context_menu', 'ERROR: (' + repr(e) + ')', 4)

    def move_stream(self, listItem):
        try:
            self.oe.dbg_log('pulseaudio::move_stream', 'enter_function', 0)
            pulse_core = self.pulse_bus.get_object(object_path='/org/pulseaudio/core1')
            pulse_core_interface = dbus.Interface(pulse_core, dbus.PROPERTIES_IFACE)
            
            streams = pulse_core_interface.Get('org.PulseAudio.Core1', 'PlaybackStreams')
            for stream in streams:
                pulse_stream = self.pulse_bus.get_object(object_path=stream)
                pulse_stream_interface = dbus.Interface(pulse_stream, dbus.PROPERTIES_IFACE)
                pulse_stream_interface.Move('org.PulseAudio.Core1.Stream',
                                            listItem.getProperty('entry'),
                                            reply_handler=self.connect_reply_handler,
                                            error_handler=self.dbus_error_handler)
            self.oe.dbg_log('pulseaudio::move_stream', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::move_stream', 'ERROR: (' + repr(e) + ')')

    def set_default(self, listItem):
        try:
            self.oe.dbg_log('pulseaudio::set_default', 'enter_function', 0)

            #self.move_stream(listItem)

            pulse_card = self.pulse_bus.get_object(object_path=listItem.getProperty('entry'))
            pulse_card_interface = dbus.Interface(pulse_card, dbus.PROPERTIES_IFACE)
            sinks = pulse_card_interface.Get('org.PulseAudio.Core1.Card', 'Sinks')
            pulse_core = self.pulse_bus.get_object(object_path='/org/pulseaudio/core1')
            pulse_core_interface = dbus.Interface(pulse_core, dbus.PROPERTIES_IFACE)
            pulse_core_interface.Set('org.PulseAudio.Core1',
                                     'FallbackSink',
                                     sinks[0],
                                     reply_handler=self.connect_reply_handler,
                                     error_handler=self.dbus_error_handler)
            self.oe.dbg_log('pulseaudio::set_default', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::set_default', 'ERROR: (' + repr(e) + ')')

    def get_profiles(self, listItem):
        try:
            self.oe.dbg_log('pulseaudio::get_profiles', 'enter_function', 0)
            values = {}
            pulse_card = self.pulse_bus.get_object(object_path=listItem.getProperty('entry'))
            pulse_card_interface = dbus.Interface(pulse_card, dbus.PROPERTIES_IFACE)
            profiles = pulse_card_interface.Get('org.PulseAudio.Core1.Card', 'Profiles')
            
            for profile in profiles:
                pulse_profile = self.pulse_bus.get_object(object_path=profile)
                pulse_profile_interface = dbus.Interface(pulse_profile, dbus.PROPERTIES_IFACE)
                profileProperties = pulse_profile_interface.GetAll('org.PulseAudio.Core1.CardProfile')
                values[profile] = {}
                for property in profileProperties:
                    values[profile][property] = profileProperties[property]
            
            self.oe.dbg_log('pulseaudio::get_profiles', 'exit_function', 0)
            return values
        except Exception, e:
            self.oe.dbg_log('pulseaudio::get_profiles', 'ERROR: (' + repr(e) + ')')

    def set_profile(self, listItem):
        try:
            self.oe.dbg_log('pulseaudio::set_profile', 'enter_function', 0)
            values = {}
            
            profiles = self.get_profiles(listItem)
            for x, profile in enumerate(profiles):
                values[x] = {
                        'profile': profile,
                        'text': profiles[profile]['Description'],
                        }
            items = []
            for key in values.keys():
                items.append(values[key]['text'])
            select_window = xbmcgui.Dialog()
            title = self.oe._(32396).encode('utf-8')
            result = select_window.select(title, items)
            if result >= 0:
                self.oe.dbg_log('pulseaudio::set_profile', 'result ' + unicode(values[result]['profile']), 0)
                pulse_profile = self.pulse_bus.get_object(object_path=listItem.getProperty('entry'))
                pulse_profile_interface = dbus.Interface(pulse_profile, dbus.PROPERTIES_IFACE)
                pulse_profile_interface.Set('org.PulseAudio.Core1.Card', 'ActiveProfile',
                                            values[result]['profile'],
                                            reply_handler=self.connect_reply_handler,
                                            error_handler=self.dbus_error_handler)
            self.oe.dbg_log('pulseaudio::set_profile', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::set_profile', 'ERROR: (' + repr(e) + ')')

    def set_value(self, listItem=None):
        try:
            self.oe.dbg_log('pulseaudio::set_value', 'enter_function', 0)
            self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
            self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True
            self.oe.dbg_log('pulseaudio::set_value', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::set_value', 'ERROR: (' + repr(e) + ')', 4)

    def connect_reply_handler(self):
        try:
            self.oe.dbg_log('pulseaudio::connect_reply_handler', 'enter_function', 0)
            self.oe.set_busy(0)
            self.menu_connections(None)
            self.oe.dbg_log('pulseaudio::connect_reply_handler', 'exit_function', 0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('pulseaudio::connect_reply_handler', 'ERROR: (' + repr(e) + ')', 4)

    def dbus_error_handler(self, error):
        try:
            self.oe.dbg_log('pulseaudio::dbus_error_handler', 'enter_function', 0)
            self.oe.set_busy(0)
            err_name = error.get_dbus_name()
            err_message = error.get_dbus_message()
            self.oe.notify('PulseAudio Error', err_message)
            self.oe.dbg_log('pulseaudio::dbus_error_handler', 'ERROR: (' + err_message + ')', 4)
            self.oe.dbg_log('pulseaudio::dbus_error_handler', 'exit_function', 0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('pulseaudio::dbus_error_handler', 'ERROR: (' + repr(e) + ')', 4)

    def get_service_path(self):
        try:
            self.oe.dbg_log('pulseaudio::get_service_path', 'enter_function', 0)
            if hasattr(self, 'winOeCon'):
                return self.winOeCon.service_path
            else:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['pulselist']).getSelectedItem()
                return listItem.getProperty('entry')
            self.oe.dbg_log('pulseaudio::get_service_path', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::get_service_path', 'ERROR: (' + repr(e) + ')', 4)

    def start_service(self):
        try:
            self.oe.dbg_log('pulseaudio::start_service', 'enter_function', 0)
            self.load_values()
            self.oe.dbg_log('pulseaudio::start_service', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::start_service', 'ERROR: (' + repr(e) + ')')

    def stop_service(self):
        try:
            self.oe.dbg_log('pulseaudio::stop_service', 'enter_function', 0)
            self.oe.dbg_log('pulseaudio::stop_service', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('pulseaudio::stop_service', 'ERROR: (' + repr(e) + ')')

    class monitor:

        def __init__(self, oeMain, parent):
            try:
                oeMain.dbg_log('pulseaudio::monitor::__init__', 'enter_function', 0)
                self.oe = oeMain
                self.signal_receivers = []
                self.signals = ['NewSink', 'SinkRemoved', 'NewSource', 'SourceRemoved']
                self.NameOwnerWatch = None
                self.parent = parent
                self.address = 'unix:path=/var/run/pulse/dbus-socket'
                self.dbusPulseBus = dbus.connection.Connection(self.address)
                self.core = self.dbusPulseBus.get_object(object_path='/org/pulseaudio/core1')
                self.oe.dbg_log('pulseaudio::monitor::__init__', 'exit_function', 0)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::__init__', 'ERROR: (' + repr(e) + ')')
                
        def signal_handler(self, data=None, sig_name=None, src_obj_path=None):
            try:
                self.oe.dbg_log('pulseaudio::monitor::signal_handler', 'enter_function', 0)
                self.oe.dbg_log('pulseaudio::monitor::signal_handler::name', repr("signal (from %s): %s %s" % (src_obj_path, sig_name, data)), 0)
                if self.parent.visible:
                    self.updateGui(object)
                self.oe.dbg_log('pulseaudio::monitor::signal_handler', 'exit_function', 0)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::signal_handler', 'ERROR: (' + repr(e) + ')', 4)

        def add_signal_receivers(self):
            try:
                self.oe.dbg_log('pulseaudio::monitor::add_signal_receivers', 'enter_function', 0)
                for signal in self.signals:
                    self.signal_receivers.append(self.dbusPulseBus.add_signal_receiver(partial(self.signal_handler, sig_name=signal), signal_name=signal, path_keyword='src_obj_path'))
                    self.core.ListenForSignal('.'.join(['org.PulseAudio.Core1', signal]), dbus.Array(signature='o'), dbus_interface='org.PulseAudio.Core1')
                self.oe.dbg_log('pulseaudio::monitor::add_signal_receivers', 'exit_function', 0)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::add_signal_receivers', 'ERROR: (' + repr(e) + ')', 4)

        def remove_signal_receivers(self):
            try:
                self.oe.dbg_log('pulseaudio::monitor::remove_signal_receivers', 'enter_function', 0)
                for signal_receiver in self.signal_receivers:
                    signal_receiver.remove()
                    signal_receiver = None
                for signal in self.signals:
                    self.core.StopListeningForSignal('.'.join(['org.PulseAudio.Core1', signal]))
                self.oe.dbg_log('pulseaudio::monitor::remove_signal_receivers', 'exit_function', 0)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::remove_signal_receivers', 'ERROR: (' + repr(e) + ')', 4)

        def updateGui(self, object):
            try:
                self.oe.dbg_log('pulseaudio::monitor::updateGui', 'enter_function', 0)
                if self.parent.visible:
                    self.parent.menu_connections(None, force=True)
                self.oe.dbg_log('pulseaudio::monitor::updateGui', 'exit_function', 0)
            except KeyError:
                self.oe.dbg_log('pulseaudio::monitor::updateGui', 'exit_function (KeyError)', 0)
                self.parent.menu_connections(None, {}, {}, force=True)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::updateGui', 'ERROR: (' + repr(e) + ')', 4)

        def forceRender(self):
            try:
                self.oe.dbg_log('pulseaudio::monitor::forceRender', 'enter_function', 0)
                focusId = self.oe.winOeMain.getFocusId()
                self.oe.winOeMain.setFocusId(self.oe.listObject['pulselist'])
                self.oe.winOeMain.setFocusId(focusId)
                self.oe.dbg_log('pulseaudio::monitor::forceRender', 'exit_function', 0)
            except Exception, e:
                self.oe.dbg_log('pulseaudio::monitor::forceRender', 'ERROR: (' + repr(e) + ')', 4)

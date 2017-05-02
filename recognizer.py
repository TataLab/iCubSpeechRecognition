#!/usr/bin/env python

"""
recognizer.py is a wrapper for pocketsphinx.
  parameters:
    ~lm - filename of language model
    ~dict - filename of dictionary
    ~mic_name - set the pulsesrc device name for the microphone input.
                e.g. a Logitech G35 Headset has the following device name: alsa_input.usb-Logitech_Logitech_G35_Headset-00-Headset_1.analog-mono
                To list audio device info on your machine, in a terminal type: pacmd list-sources
  publications:
    ~output (std_msgs/String) - text output
  services:
    ~start (std_srvs/Empty) - start speech recognition
    ~stop (std_srvs/Empty) - stop speech recognition
"""



import pygtk
pygtk.require('2.0')
import gtk

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

import ctypes

import os
import commands

import yarp

yarp.Network.init()

rf = yarp.ResourceFinder()
rf.setVerbose(True);
rf.setDefaultContext("myContext");
rf.setDefaultConfigFile("default.ini");

p = yarp.BufferedPortBottle()
p.open("/speech");

class recognizer(object):
    """ GStreamer based speech recognizer. """

    def __init__(self):
        # Start node

        self._device_name_param = "~mic_name"  # Find the name of your microphone by typing pacmd list-sources in the terminal
        self._lm_param = "~lm"
        self._dic_param = "~dict"

        # Configure mics with gstreamer launch config
        
        self.launch_config = 'autoaudiosrc'

        

        self.launch_config += " ! audioconvert ! audioresample " \
                            + '! vader name=vad auto-threshold=true ' \
                            + '! pocketsphinx name=asr ! fakesink'

        # Configure ROS settings
        self.started = False
        self.start_recognizer()

    def start_recognizer(self):
        

        self.pipeline = gst.parse_launch(self.launch_config)
        self.asr = self.pipeline.get_by_name('asr')
        self.asr.connect('partial_result', self.asr_partial_result)
        self.asr.connect('result', self.asr_result)
        self.asr.set_property('configured', True)
        self.asr.set_property('dsratio', 1)

        lm = '/media/sd_storage/hello/model/voice_cmd.lm'
        dic = '/media/sd_storage/hello/model/voice_cmd.dic'

        self.asr.set_property('lm', lm)
        self.asr.set_property('dict', dic)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus_id = self.bus.connect('message::application', self.application_message)
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.started = True

    def pulse_index_from_name(self, name):
        output = commands.getstatusoutput("pacmd list-sources | grep -B 1 'name: <" + name + ">' | grep -o -P '(?<=index: )[0-9]*'")

        if len(output) == 2:
            return output[1]
        else:
            raise Exception("Error. pulse index doesn't exist for name: " + name)

    def stop_recognizer(self):
        if self.started:
            self.pipeline.set_state(gst.STATE_NULL)
            self.pipeline.remove(self.asr)
            self.bus.disconnect(self.bus_id)
            self.started = False

    def shutdown(self):
        """ Delete any remaining parameters so they don't affect next launch """
        p.close();
        yarp.Network.fini();
        """ Shutdown the GTK thread. """
        gtk.main_quit()

    def start(self, req):
        self.start_recognizer()
        print("recognizer started")
        return EmptyResponse()

    def stop(self, req):
        self.stop_recognizer()
        print("recognizer stopped")
        return EmptyResponse()

    def asr_partial_result(self, asr, text, uttid):
        """ Forward partial result signals on the bus to the main thread. """
        struct = gst.Structure('partial_result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def asr_result(self, asr, text, uttid):
        """ Forward result signals on the bus to the main thread. """
        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """ Receive application messages from the bus. """
        msgtype = msg.structure.get_name()
        if msgtype == 'partial_result':
            self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
        if msgtype == 'result':
            self.final_result(msg.structure['hyp'], msg.structure['uttid'])

    def partial_result(self, hyp, uttid):
        """ Delete any previous selection, insert text and select it. """
        print("Partial: " + hyp)

    def final_result(self, hyp, uttid):
        """ Insert the final result. """
        #    self.pub.publish(msg)
        bottle = p.prepare()
        bottle.clear()
        bottle.add(hyp.encode('utf-8'))
        print ("Sending", bottle.toString())
        p.write()

if __name__ == "__main__":
    start = recognizer()
    gtk.main()


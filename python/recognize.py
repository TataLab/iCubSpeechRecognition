import yarp
from pprint import pprint
import pyaudio
import numpy as np
import webrtcvad
import wave
import requests
import threading
import json

vad = webrtcvad.Vad()

vad.set_mode(3)

yarp.Network.init()
writePort = yarp.BufferedPortBottle()
writePort.open('/speech/text')

class DataProcessor(yarp.PortReader):
    def __init__(self):
        yarp.PortReader.__init__(self)
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.speechBuffer = []
        self.prevBuffer = []
        self.silent=0;

    def read(self,connection):
        #print("in DataProcessor.read")
        if not(connection.isValid()):
            print("Connection shutting down")
            return False
        s = yarp.Sound()

        #print("Trying to read from connection")
        ok = s.read(connection)
        if not(ok):
            print("Failed to read input")
            return False
        data = [];

        if self.stream is None:
            self.stream = self.audio.open(
                format=self.audio.get_format_from_width(s.getBytesPerSample()),
                channels=s.getChannels(),
                rate=s.getFrequency(),
                output=True,
                frames_per_buffer=s.getSamples()
            );

        for i in range(s.getSamples()):
            data.append(s.get(i, 0));
            if s.getChannels() == 2:
                data.append(s.get(i, 1));

        data = np.array(data, dtype='<i2');

        speechPresent = False;

        for i in range(10):
            if vad.is_speech(data[i:i+160].tobytes(), 16000):
                speechPresent = True;

        print 'speech present: ' + str(speechPresent);
        #print data

        if self.silent < 20:
            if not speechPresent:
                self.silent += 1;

            self.speechBuffer.extend(data);
        else:
            self.silent = 0;

            if len(self.speechBuffer) > s.getChannels()*s.getFrequency()*s.getBytesPerSample():
                print("speech detected, recognizing...")

                try:
                    threading.Thread(target=self.recognize, kwargs={'s': s, 'speechBuffer': self.speechBuffer}).start()
                except Exception as e:
                    print e
            #self.stream.write(data.tobytes())
            self.speechBuffer = []
        self.prevBuffer = data

    def recognize(args, s, speechBuffer):
        waveFile = wave.open('/tmp/test.wav', 'wb')
        waveFile.setnchannels(s.getChannels())
        waveFile.setsampwidth(s.getBytesPerSample())
        waveFile.setframerate(s.getFrequency())
        waveFile.writeframes(b''.join(np.array(speechBuffer).tobytes()))
        waveFile.close()

        url = 'http://localhost:8080/client/dynamic/recognize'
        r = requests.post(url,
                          data=open('/tmp/test.wav', 'rb'),
                          headers={'Content-Type': 'audio/x-wav'});

        txt = r.text;
        res = json.loads(txt);
        speechText = res[u'hypotheses'][0][u'utterance']
        print speechText

        bottle = writePort.prepare()
        bottle.clear()
        bottle.addString(str(speechText))
        writePort.write()

speechAudioPort = yarp.Port()
r = DataProcessor()
speechAudioPort.setReader(r)
speechAudioPort.open("/speech/audio");

yarp.Network.connect("/filtered", "/speech/audio");

yarp.Time.delay(100)
print("Test program timer finished")

yarp.Network.fini();

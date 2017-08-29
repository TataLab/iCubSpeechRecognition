import yarp
from pprint import pprint
import pyaudio
import numpy as np

yarp.Network.init()

class DataProcessor(yarp.PortReader):
    def __init__(self):
        yarp.PortReader.__init__(self)
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def read(self,connection):
        print("in DataProcessor.read")
        if not(connection.isValid()):
            print("Connection shutting down")
            return False
        s = yarp.Sound()

        print("Trying to read from connection")
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
        #print data
        self.stream.write(data.tobytes())

        free = self.stream.get_write_available()
        if free > s.getSamples():
            tofill = free - s.getSamples();
            self.stream.write(chr(0) * tofill*2)



p = yarp.Port()
r = DataProcessor()
p.setReader(r)
p.open("/python");

yarp.Network.connect("/filtered", "/python");

yarp.Time.delay(100)
print("Test program timer finished")

yarp.Network.fini();

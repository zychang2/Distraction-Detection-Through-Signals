import platform
import sys
import os

osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
if platform.mac_ver()[0] != "":
    import subprocess
    from os import linesep

    p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8").split(str("\t"))[2].split(linesep)[0]
    if result.startswith("12."):
        print("macOS version is Monterrey!")
        osDic["Darwin"] = "MacOS/Intel310"
        if (
            int(platform.python_version().split(".")[0]) <= 3
            and int(platform.python_version().split(".")[1]) < 10
        ):
            print(f"Python version required is ≥ 3.10. Installed is {platform.python_version()}")
            exit()


sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

path_name = ''


class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        plux.MemoryDev.__init__(address)
        self.duration = 0
        self.frequency = 0
    
    def write_frame(self, file, nSeq, *data):
        line = str(nSeq) + ', ' + ', '.join(str(x) for x in data) + '\n'
        file.write(line)

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        with open(path_name, 'a') as file:
            self.write_frame(file, nSeq, *data)
        if nSeq % 1000 == 0:
            print(nSeq, *data)
        return nSeq > self.duration * self.frequency


# example routines


def exampleAcquisition(
    address="BTH00:21:08:01:10:DE",
    duration=60,
    frequency=1000,
    code=0x3F,
    num=0,
):  # time acquisition for each frequency
    """
    Example acquisition.

    Supported channel number codes:
    {1 channel - 0x01, 2 channels - 0x03, 3 channels - 0x07
    4 channels - 0x0F, 5 channels - 0x1F, 6 channels - 0x3F
    7 channels - 0x7F, 8 channels - 0xFF}

    Maximum acquisition frequencies for number of channels:
    1 channel - 8000, 2 channels - 5000, 3 channels - 4000
    4 channels - 3000, 5 channels - 3000, 6 channels - 2000
    7 channels - 2000, 8 channels - 2000
    """
    global path_name
    path_name = f'Data_{num}.txt'
    with open(path_name, 'w') as file:
        pass
    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    if isinstance(code, str):
        code = int(code, 16)  # From hexadecimal str to int
    print("Start recording...")
    device.start(device.frequency, code, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    # print(device.getNumChannels())
    device.stop()
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    # print("Found: ", plux.BaseDev.findDevices('BTH'))
    exampleAcquisition(*sys.argv[1:], num=0)

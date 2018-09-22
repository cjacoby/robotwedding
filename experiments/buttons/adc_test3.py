import time
import sys
import spidev

spi = spidev.SpiDev()
spi.open(0, 1)

def readAdc(channel):
    if ((channel > 7) or (channel < 0)):
        return -1
    r = spi.xfer2(buildReadCommand(channel))
    return processAdcValue(r)

if __name__ == '__main__':
    try:
        while True:
            val = readAdc(0)
            print "ADC Result: ", str(val)
            time.sleep(1)
    except KeyboardInterrupt:
        spi.close()
        sys.exit(0)

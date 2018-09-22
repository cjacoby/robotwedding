# Importing modules
import mcp3008
import time

t0 = time.time()
with mcp3008.MCP3008(device=0) as adc:
    try:
        while True:
            c0, c1 = adc.read([mcp3008.CH0, mcp3008.CH1], norm=True)
            print("{:4} {:4}  {:.4f}       \r".format(c0, c1, time.time() - t0), end="")
#            data = adc.read_all(norm=True)
#            print(data, time.time() - t0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print()
        print("Closing...")

"""A long, valid Python program that ignores SIGINT."""
import signal
from time import sleep

signal.signal(signal.SIGINT, lambda x, y, z: None)

print("Starting")
for i in range(10):
    print(i)
    sleep(1)
print("Finished")

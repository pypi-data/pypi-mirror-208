import time
import sys
def TP(saniye, metin):
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(int(saniye)/len(metin))
    print("")
def P(metin):
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(0.001)
    print("")
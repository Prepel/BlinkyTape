import time
import random
import sys
import signal
sys.path.append("../")
from BlinkyTape import BlinkyTape


def signal_handler(signal, frame):
    print('Exit()')
    blinkyTape.clear()
    sys.exit(0)


class lightFlow(object):

    if(len(sys.argv) > 2):
        rangeSize = int(sys.argv[2])
    else:
        rangeSize = 25

    currentPixel = 0
    pixelDirection = 1

    red = 127
    green = 127
    blue = 127

    def __init__(self, blinkyTape):
        self.blinkyTape = blinkyTape

    def frame(self, explain):
        if(explain):
            self.explain()

        self.blinkyTape.setPixel(self.currentPixel, self.red, self.green, self.blue, True)

        self.determineNextPixel()
        self.determineNextColors()

    def determineNextPixel(self):
        if(self.currentPixel == 59 and self.pixelDirection == 1):
            self.pixelDirection = -1
        elif(self.currentPixel == 0 and self.pixelDirection == -1):
            self.pixelDirection = 1

        self.currentPixel = self.currentPixel + self.pixelDirection

    def determineNextColors(self):
        randomred = random.randrange(self.rangeSize * -1, self.rangeSize)
        self.red = self.calculateNextColorAmount(self.red, randomred)

        randomgreen = random.randrange(self.rangeSize * -1, self.rangeSize)
        self.green = self.calculateNextColorAmount(self.green, randomgreen)

        randomblue = random.randrange(self.rangeSize * -1, self.rangeSize)
        self.blue = self.calculateNextColorAmount(self.blue, randomblue)

    def calculateNextColorAmount(self, currentAmount, changeAmount):
        newAmount = currentAmount + changeAmount
        if(newAmount >= 255):
            return 255
        elif(newAmount <= 0):
            return 0
        else:
            return newAmount

    def explain(self):
        print "Showing RGB({},{},{}) on LED {}".format(self.red, self.green, self.blue, self.currentPixel)


blinkyTape = BlinkyTape("/dev/tty.usbmodem1441")
blinkyTape.clear()

signal.signal(signal.SIGINT, signal_handler)

lightFlow = lightFlow(blinkyTape)
while True:
    lightFlow.frame(explain=True)

    if(len(sys.argv) > 1):
        time.sleep(float(sys.argv[1]))
    else:
        time.sleep(random.uniform(0.01, 0.1))

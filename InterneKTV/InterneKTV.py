from ConfigParser import SafeConfigParser
import datetime
import time
import glob
import optparse
import pymysql
import serial
import math

class InterneKTV(object):

    mysql_host          = ""
    mysql_username      = ""
    mysql_password      = ""
    mysql_database      = ""
    mysql_schema        = ""
    mysql_port          = ""
    retrieval_interval  = ""

    current_thumbs_up = 0
    current_thumbs_down = 0

    previous_thumbs_up = 0
    previous_thumbs_down = 0

    blinkyTape = ""
    totalAmountPercentage = 0

    def __init__(self, blinkyTape):
        self.blinkyTape = blinkyTape

    def loadConfigurationFile(self, path):
        configParser = SafeConfigParser()
        configParser.read(path)

        self.mysql_host = configParser.get('MySQL', 'mysql_host')
        self.mysql_username = configParser.get('MySQL', 'mysql_username')
        self.mysql_password = configParser.get('General', 'mysql_password')
        self.mysql_port = configParser.get('MySQL', 'mysql_port')
        self.mysql_schema = configParser.get('MySQL', 'mysql_schema')

        self.retrieval_interval = configParser.get('General', 'data_retrieval_interval')

    def retrieveInformation(self):

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='blinkytape',
                                     charset='utf8')

        cur = connection.cursor()

        cur.execute("SELECT SUM(positive_vote) as thumbs_up, SUM(negative_vote) as thumbs_down FROM satisfaction");

        row = cur.fetchone()

        self.current_thumbs_up = row[0]
        self.current_thumbs_down = row[1]

        cur.close()
        connection.close()

    def processSatisfactionData(self):
        red = 190
        green = 120
        if (int(self.previous_thumbs_up) == 0 & int(self.previous_thumbs_down) == 0):
            self.previous_thumbs_down = self.current_thumbs_down
            self.previous_thumbs_up = self.current_thumbs_up

        else:
            thumbsUpDifference = 0
            thumbsDownDifference = 0

            if (int(self.current_thumbs_up) > int(self.previous_thumbs_up)):
                thumbsUpDifference = self.current_thumbs_up - self.previous_thumbs_up

            if (int(self.current_thumbs_down) > int(self.previous_thumbs_down)):
                thumbsDownDifference = self.current_thumbs_down - self.previous_thumbs_down

            if (thumbsUpDifference > thumbsDownDifference):
                print("Difference in thumbsup")
                self.blinkyTape.clear()
                for num in range(0, 31):
                    print("Difference in thumbsup")
                    self.blinkyTape.setPixel(num, 0, 255, 0, True)
                    self.blinkyTape.setPixel(self.blinkyTape.getSize() - (num) - 1, 0, 255, 0, True)
                    time.sleep(0.05)
                for num in range(0, 5):
                    self.blinkyTape.displayColor(0, 0, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(0, 255, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(0, 0, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(0, 255, 0)
                    time.sleep(0.5)

                time.sleep(1)

                for num in range(0, 31):
                    self.blinkyTape.setPixel(num, 0, 0, 0, True)
                    self.blinkyTape.setPixel(self.blinkyTape.getSize() - (num) - 1, 0, 0, 0, True)
                    time.sleep(0.05)

            elif (thumbsDownDifference > thumbsUpDifference):
                print("Difference in thumbsdown")
                self.blinkyTape.clear()
                for num in range(0, 31):
                    self.blinkyTape.setPixel(num, 255, 0, 0, True)
                    self.blinkyTape.setPixel(self.blinkyTape.getSize() - (num) - 1, 255, 0, 0, True)
                    time.sleep(0.05)
                for num in range(0, 5):
                    self.blinkyTape.displayColor(0, 0, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(255, 0, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(0, 0, 0)
                    time.sleep(0.5)
                    self.blinkyTape.displayColor(255, 0, 0)
                    time.sleep(0.5)

                time.sleep(1)

                for num in range(0, 31):
                    self.blinkyTape.setPixel(num, 0, 0, 0, True)
                    self.blinkyTape.setPixel(self.blinkyTape.getSize() - (num) - 1, 0, 0, 0, True)
                    time.sleep(0.05)

            time.sleep(1)

            totalAmountPercentage = math.ceil((float(self.current_thumbs_up) / (
            float(self.current_thumbs_up) + float(self.current_thumbs_down))) * 60)
            print("Showing score")
            print(totalAmountPercentage)
            for num in range(0, int(totalAmountPercentage)):
                self.blinkyTape.setPixel(num, 0, green, 0, True)
                time.sleep(0.05)

            for num in range(0, 60 - (int(totalAmountPercentage))):
                self.blinkyTape.setPixel(59 - (num), red, 0, 0, True)
                time.sleep(0.05)

                self.previous_thumbs_down = self.current_thumbs_down
                self.previous_thumbs_up = self.current_thumbs_up


class BlinkyTape(object):
    def __init__(self, port, ledCount=60):
        self.port = port
        self.ledCount = ledCount
        # Initialise the LED buffer
        self.led = []
        for i in range(0, self.ledCount):
            self.led.append([0, 0, 0])
        self.serial = serial.Serial(port, 115200)
        self.sendUpdate()

    # Set a specified pixel to a specified RGB value in our buffer.
    # If final argument==True, then push update to the strip
    def setPixel(self, pixel, r, g, b, autoUpdate=False):
        self.led[pixel] = [r, g, b]
        if autoUpdate:
            self.sendUpdate()

    # Update the strip to match our current buffer
    def sendUpdate(self):
        data = ""
        for i in range(0, self.ledCount):
            for c in range(3):
                if self.led[i][c] > 254:
                    self.led[i][c] = 254
                if self.led[i][c] < 0:
                    self.led[i][c] = 0
                data += chr(self.led[i][c])
        data += chr(0) + chr(0) + chr(255)
        self.serial.write(data)
        self.serial.flush()
        self.serial.flushInput()

    # Turn off all LEDs
    def clear(self):
        self.displayColor(0, 0, 0)

    # Set all LEDs to the same colour
    def displayColor(self, r, g, b):
        for i in range(0, self.ledCount):
            self.setPixel(i, r, g, b)
        self.sendUpdate()

    # Return number of LEDs in our strip
    def getSize(self):
        return self.ledCount

    # Attempt to turn off and close serial connection gracefully on object destruction
    def __del__(self):
        self.clear()
        self.serial.close()


blinkyTape = BlinkyTape("/dev/tty.usbmodem1441")
#blinkyTape.clear()
interneKTV = InterneKTV(blinkyTape)
starttime = time.time()

while True:
    day_of_week = datetime.date.today().weekday()  # 0 is Monday, 6 is Sunday
    currenttime = datetime.datetime.now().time()

    interneKTV.retrieveInformation()
    interneKTV.processSatisfactionData()
    
    time.sleep(5.0 - ((time.time() - starttime) % 5.0))

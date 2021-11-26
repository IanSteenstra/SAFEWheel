
#run code in background without seeing output (full code with ians)
#fix wires


import datetime
from google.cloud import storage
import time
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
DEBUG = 1
#elapsed_time = 0

def getTime():
    now = str(datetime.datetime.now())
    with open("hands-time.txt","a+") as f:
        f.write("|")
    	f.write(now)
    f.close()

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False) # start clock low
    GPIO.output(cspin, False) # bring CS low
    commandout = adcnum
    commandout |= 0x18 # start bit + single-ended bit
    commandout <<= 3 # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1
    GPIO.output(cspin, True)
    adcout >>= 1 # first bit is 'null' so drop it
    return adcout

def main():

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/SAFEWheel-e3260c10b7e8.json"
    project = 'safewheel-219707'
    storage_client = storage.Client(project=project)
    bucket = storage_client.get_bucket('safewheel_data')

    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25


    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    # 10k trim pot connected to adc #0
    potentiometer_adc = 0;
    pot_adc2 = 1;

    last_read = 0 # this keeps track of the last potentiometer value
    tolerance = 5 # to keep from being jittery we'll only change
    # volume when the pot has moved more than 5 'couunts'

    last_read2 = 0 # this keeps track of the last potentiometer value
    tolerance2 = 5 # to keep from being jittery we'll only change


    #calibrate sensor 1
    first_read = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    second_read = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    third_read = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)

    #calibrate sensor 2
    first_read2 = readadc(pot_adc2, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    second_read2 = readadc(pot_adc2, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    third_read2 = readadc(pot_adc2, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)



    while True:
        # we'll assume that the pot didn't move
        trim_pot_changed = False
        trim_pot_changed2 = False
        
        # read the analog pin
        trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        trim_pot2 = readadc(pot_adc2, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        pot_adjust = abs(trim_pot - last_read)
        pot_adjust2 = abs(trim_pot2 - last_read2)
        
        if DEBUG:
            print("trim_pot:", trim_pot)
            print("pot_adjust:", pot_adjust)
            print("last_read", last_read)
            
            print("trim_pot2:", trim_pot2)
            print("pot_adjust2:", pot_adjust2)
            print("last_read2", last_read2)
            
            
        if ( pot_adjust > tolerance ):
            trim_pot_changed = True
            
        if ( pot_adjust2 > tolerance2 ):
            trim_pot_changed2 = True        
            
            
        if DEBUG:
            print("trim_pot_changed", trim_pot_changed)
            print("trim_pot_changed2", trim_pot_changed2)
            
            
        if ( trim_pot_changed ):
            set_volume = trim_pot / 10.24 # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
            set_volume = round(set_volume) # round out decimal value
            if DEBUG:
               # print("set_volume", set_volume)
                print("tri_pot_changed", set_volume)
            # save the potentiometer reading for the next loop
            last_read = trim_pot
        # hang out and do nothing for a half second
        time.sleep(0.5)
        
        
        
        if ( trim_pot_changed2 ):
            set_volume2 = trim_pot2 / 10.24 # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
            set_volume2 = round(set_volume2) # round out decimal value
            set_volume2 = int(set_volume2) # cast volume as integer
            if DEBUG:
               # print("set_volume2", set_volume2)
                print("tri_pot_changed2", set_volume2)
            # save the potentiometer reading for the next loop
            last_read2 = trim_pot2
        # hang out and do nothing for a half second
        time.sleep(0.5)    
        
        
        if ((trim_pot > third_read+10) and (trim_pot2 > third_read2+10)):
           # elapsed_time += time.time() - start_time
            print ("BUZZER off")
            GPIO.output(27,GPIO.LOW)
            

        if ((trim_pot < third_read+10) or (trim_pot2 < third_read2+10)):
            #start_time = time.time()
            print ("BUZZER on")
            GPIO.output(27,GPIO.HIGH)       
            time.sleep(0.5)
	    getTime()
            hand = bucket.blob('Hand Time')
            hand.upload_from_filename("hands-time.txt")
            GPIO.output(27,GPIO.LOW)
            time.sleep(0.5)
		

       # print(elapsed_time)

if __name__ == '__main__':
    
    main()

    
    
    
        
import RPi.GPIO as GPIO # Import Raspberry Pi libraries
import sys # For closing application
import math
import os
import threading # Handle counts
import time # Handle threading sleeps
from sandals import * # For easy display

## Variables
TEST_PIN = 10
# 0: idle, 1: button beeing pressed down, 2: waiting for button release,
# 3: waiting for button hit
current_mode = 0

# Window variables
current = ""
one = ""
two = ""
three = ""
four = ""
five = ""
six = ""
seven = ""
eight = ""
nine = ""

#Leaderboard variables
leaderboard = [("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99"), ("", "99:99")]

##Setup GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD) #Physical pin numbering

## Pin setup
GPIO.setup(TEST_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # Set up pin as input with default to off


# Create a window for the leaderboard
def init_leaderboard():
    main_window = window("Leaderboard")
    # Handle main window closing
    main_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    #Make main window fit screen size
    width, height = main_window.winfo_screenwidth(), main_window.winfo_screenheight()
    main_window.geometry('%dx%d+0+0' % (width, height))
    
    with main_window:
        global current
        global one
        global two
        global three
        global four
        global five
        global six
        global seven
        global eight
        global nine
        
        with stack(pady = 35):
            current = label("Hold button to start", font = "Verdana 55 underline")
        
        with stack(pady = 25):
            label("Leaderboard", font = "Verdana 75 bold")
        
        with stack(pady = 10):
            one = label ("1.     99:99     Lucas Romier", font = "Verdana 30")
            two = label ("2.     99:99     Lucas Romier", font = "Verdana 30")
            three = label ("3.     99:99     Lucas Romier", font = "Verdana 30")
            four = label ("4.     99:99     Lucas Romier", font = "Verdana 30")
            five = label ("5.     99:99     Lucas Romier", font = "Verdana 30")
            six = label ("6.     99:99     Lucas Romier", font = "Verdana 30")
            seven = label ("7.     99:99     Lucas Romier", font = "Verdana 30")
            eight = label ("8.     99:99     Lucas Romier", font = "Verdana 30")
            nine = label ("9.     99:99     Lucas Romier", font = "Verdana 30")
            
            #Render saved values
            render_leaderboard()


def load_stored_leaderboard():
    global leaderboard
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    #Create file if not exists
    if not os.path.isfile(os.path.abspath("leaderboard.save")):
        open(os.path.abspath("leaderboard.save"), "w+").close()
    
    with open(os.path.abspath("leaderboard.save"), "r") as read:
        contents = read.readlines()
        
        for i in range(len(contents)):
            content = contents[i]
            if content is not None:
                content = content.replace("\n", "").replace("\r", "")
                sep = content.split(":")
                name = sep[0]
                sec = sep[1]
                nano = sep[2]
                    
                #Enter in leaderboard
                leaderboard.insert(i, (name, sec + ":" + nano))
                #Delete also last entry
                del leaderboard[-1]
        read.close()


def store_leaderboard():
    global leaderboard
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with open(os.path.abspath("leaderboard.save"), "w+") as write:
        #Write the leaderboard values into the file
        for score in leaderboard:
            write.write(score[0] + ":" + score[1] + "\r\n")
        write.close();
    print("done")


#Overwrite the leaderboard
def render_leaderboard():
    global leaderboard
    
    global one
    global two
    global three
    global four
    global five
    global six
    global seven
    global eight
    global nine
    
    one.text = "1.     " + leaderboard[0][1] + "     " + leaderboard[0][0]
    two.text = "2.     " + leaderboard[1][1] + "     " + leaderboard[1][0]
    three.text = "3.     " + leaderboard[2][1] + "     " + leaderboard[2][0]
    four.text = "4.     " + leaderboard[3][1] + "     " + leaderboard[3][0]
    five.text = "5.     " + leaderboard[4][1] + "     " + leaderboard[4][0]
    six.text = "6.     " + leaderboard[5][1] + "     " + leaderboard[5][0]
    seven.text = "7.     " + leaderboard[6][1] + "     " + leaderboard[6][0]
    eight.text = "8.     " + leaderboard[7][1] + "     " + leaderboard[7][0]
    nine.text = "9.     " + leaderboard[8][1] + "     " + leaderboard[8][0]


def was_valid_run():
    yes_no = input("Valid run? [Y/N]: ")
    if yes_no.lower() == "y" or yes_no.lower() == "yes":
        return True
    elif yes_no.lower() == "n" or yes_no.lower() == "no":
        return False
    else:
        return was_valid_run()


def update_leaderboard(score_sec, score_nano):
    global leaderboard
    
    in_highscore = False
    
    for i in range(len(leaderboard)):
        score = leaderboard[i]
        name = score[0]
        time_unit = score[1]
        
        sep = time_unit.split(":")
        sec = int(sep[0])
        nano = int(sep[1])
        
        #Check if better than current
        if (int(score_sec) < sec) or (int(score_sec) == sec and int(score_nano) < nano):
            if was_valid_run() == True:
                #Ask for name
                new_name = input("Enter name: ")
                #Insert at current position
                leaderboard.insert(i, (new_name, score_sec + ":" + score_nano))
                #Delete last item
                del leaderboard[-1]
                #Render leaderboard again
                render_leaderboard()
                #Store the new data in a file
                store_leaderboard()
                #Update information
                in_highscore = True
            
            break
    print("")
    
    #Show scores little longer if not in highscore
    if in_highscore == False:
        time.sleep(5) #Sleep for 5 seconds
        
    #Then overwrite text to def
    current.text = "Hold button to start"


# When button is pressed or released
def button_state_changed(channel):
    global current_mode
    global current
    
    if GPIO.input(TEST_PIN):
        #print("Button was pushed")
        
        # Countdown initiated from idle mode
        if current_mode == 0:
            # Set mode to countdown
            current_mode = 1
            # Start countdown
            threading.Thread(target = start_countdown).start()
        elif current_mode == 3:
            # Stop timer by changing mode
            current_mode = 0
            #Check for new highscore
            sep = current.text.split(":")
            update_leaderboard(sep[0], sep[1])
    else:
        #print("Button was released")
        
        # Button was released before countdown was done
        if current_mode == 1:
            #Reset
            current_mode = 0
            current.text = "Hold the button to start"
        elif current_mode == 2:
            current_mode = 3
            # Start countup
            threading.Thread(target = start_countup).start()


# Handle start countdown
def start_countdown():
    global current_mode
    global current
    
    if current_mode == 1: 
        current.text = "You may start in"
        time.sleep(1)
        if current_mode == 1:
            current.text = "3"
            time.sleep(0.4)
            if current_mode == 1:
                current.text = "2"
                time.sleep(0.4)
                if current_mode == 1:
                    current.text = "1"
                    time.sleep(0.4)
                    if current_mode == 1:
                        current.text = "Release button to start"
                        # Set to counting mode
                        current_mode = 2


def start_countup():
    global current_mode
    global current
    
    elapsed = 0
    last = int(round(time.time() * 1000))
    while current_mode == 3:
        # Count time difference since last time
        now = int(round(time.time() * 1000))
        
        elapsed += now - last
        
        last = now

        # Update timer counter
        to_seconds = int(math.floor(elapsed / 1000))
        to_centi = str(int(round(elapsed / 1000 - to_seconds, 2) * 100))
        #Always keep length at 3
        while len(to_centi) < 3:
            to_centi = "0" + to_centi
        
        current.text = str(to_seconds) + ":" + to_centi


## Listen for GPIO events
GPIO.add_event_detect(TEST_PIN, GPIO.BOTH, callback = button_state_changed)

#Load saved leaderboard
load_stored_leaderboard()

# Do all the grapical stuff
init_leaderboard()
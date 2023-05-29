import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
import PySimpleGUI as sg
import threading

GPIO.setwarnings(False)

"""
    les variables globales et autres utiles au programme
"""

def_font = "default 10"
str_bold = " bold"
str_udl = " underline"
str_door_open = "Pourcentage d’ouverture de la porte:\n\n"

global counter
global temperature
global distance
global temp_difference

global get_update
global isAutomatique

DHTPin = 11
trigPin = 16
echoPin = 18
# define pins connected to four phase ABCD of stepper motor
motorPins = (12, 36, 38, 22)

MAX_DISTANCE = 50  # define the maximum measured distance(cm)
# calculate timeout(μs) according to the maximum measured
timeOut = MAX_DISTANCE*60

CCWStep = (0x01, 0x02, 0x04, 0x08)  # rotating anticlockwise
CWStep = (0x08, 0x04, 0x02, 0x01)  # rotating clockwise

MOTOR_SPEED = 4
MOTOR_STEPS = 10

MIN_DOOR_CM = 3
MAX_DOOR_CM = 9

DIRECTION_CW = 0 
DIRECTION_CCW = 1

CHECK_COUNT = 175
MAX_TEMP_READ = 35

# =================== distance ===================


def pulseIn(pin, level, timeOut):  # function pulseIn: obtain pulse time of a pin
    t0 = time.time()
    while (GPIO.input(pin) != level):
        if ((time.time() - t0) > timeOut*0.000001):
            return 0
    t0 = time.time()
    while (GPIO.input(pin) == level):
        if ((time.time() - t0) > timeOut*0.000001):
            return 0
    pulseTime = (time.time() - t0)*1000000
    return pulseTime


def getSonar():  # get the measurement results of ultrasonic module,with unit: cm
     GPIO.output(trigPin, GPIO.HIGH)  # make trigPin send 10us high level
     time.sleep(0.00001)  # 10us
     GPIO.output(trigPin, GPIO.LOW)
     pingTime = pulseIn(echoPin, GPIO.HIGH, timeOut) #read plus time of echoPin
     distance = pingTime * 340.0 / 2.0 / 10000.0  # the sound speed is 340m/s, and
     return distance


# =================== distance ===================


# =================== motor ===================

# as for four phase Stepper Motor, four steps is a cycle. the function is used to drive the
# Stepper Motor clockwise or anticlockwise to take four steps
def moveOnePeriod(direction, ms):
     for j in range(0, 4, 1): # cycle for power supply order
         for i in range(0, 4, 1): # assign to each pin
             if (direction == 1):  # power supply order clockwise
                 GPIO.output(motorPins[i], ((CCWStep[j] == 1 <<i) and GPIO.HIGH or GPIO.LOW))
             else:  # power supply order anticlockwise
                 GPIO.output(motorPins[i], ((CWStep[j] == 1 <<i) and GPIO.HIGH or GPIO.LOW))
         if(ms < 3): # the delay can not be less than 3ms, otherwise it will exceed speed
                 # limit of the motor
             ms = 3
         time.sleep(ms*0.001)

# continuous rotation function, the parameter steps specify the rotation cycles, every four
# steps is a cycle


def moveSteps(direction, ms, steps):
    for i in range(steps):
        moveOnePeriod(direction, ms)

# function used to stop motor


def motorStop():
    for i in range(0, 4, 1):
        GPIO.output(motorPins[i], GPIO.LOW)

# =================== motor ===================

# =================== interface ===================

"""
    cette methode defini l'interface avec ses elements
"""
def user_interface():

    sg.theme('DefaultNoMoreNagging')

    lay_title = [
        sg.Push(), sg.Text('Contrôle d’une porte d’aération d’une serre', font = def_font+str_bold), sg.Push()
    ]

    lay_control = [
        [sg.Text('Température ambiante : ', font = def_font+str_bold), sg.Text('31 °C', key="-STR_TEMP-" , font = def_font)],
        [sg.Text("Contrôle", font=def_font+str_bold+str_udl), sg.Text(":", font= def_font), sg.Button("Automatique", button_color=('black', 'light gray'), key="AUTOMATIQUE_BTN")],
        [sg.Text(pad=(50, 0)), sg.Button("Manuelle", button_color=('black', 'light gray'), key="MANUELLE_BTN"), sg.Input(enable_events=True, size=(4,1), key='-STR_INPUT_PCT-', justification='center'),sg.Text('%', font = def_font)],
        [sg.Button("Ouvrir la porte", button_color=('black', 'light gray'), pad=(0, 30), key="-OPEN_BTN-"), sg.Button("Fermer la porte", key="-CLOSE_BTN-", button_color=('black','light gray'), pad=(25,30))]
    ]

    lay_progress = [
        [sg.Text(pad=(20, 0)), sg.ProgressBar(max_value=100, orientation="v", size=(10, 50), border_width=2, key="-PROGRESS_BAR-", bar_color=["green", "grey"]),
         sg.Text(str_door_open, font= def_font+str_bold, size=(12, 0), key="-STR_OPEN_DOOR_PCT-", justification="center"),
         ]
    ]

    lay_motor = [
        [sg.Text("Moteur", font=def_font+str_bold+str_udl), sg.Text(":", font=def_font)],
        [sg.Text('Direction :', font = def_font+str_bold), sg.Text('Gauche|Droite', font = def_font), sg.Text(pad=(50,0)), sg.Text('Vitesse :', font = def_font+str_bold),sg.Text('20 tour/min', font = def_font)]
    ]

    lay_vsep = [
        sg.VSeparator()
    ]

    layout = [

        lay_title,
        [
            sg.Column(lay_control),
            lay_vsep,
            sg.Column(lay_progress)
        ],
        lay_motor
    ]

    window = sg.Window('TP1: Omar - Khalil', layout, size=(600, 300), grab_anywhere=True, finalize=True)

    return window


# =================== interface ===================


# =================== utilities ===================

"""
    cette methode permet de verfifer si le contenu (string) est numerique
"""
def check_number(str_wanted):
    return str_wanted.isnumeric()

"""
    cette methode permet de faire l'attente de mise a jour a chaque seconde
"""
def get_updated_element(window, sleep_time):
    time.sleep(sleep_time)
    window.write_event_value("can_update_element", None)

"""
    cette methode permet de faire une verfication du DHT11 et de retourner la temperature
"""
def getTemp(dht):
    for i in range(0, 15):
        # read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        chk = dht.readDHT11()
        # read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):
            break
    return dht.temperature

pct = 0
"""
    cette methode permet de fermer la porte selon un pourcentage et si c'est le mode est automatique ou non
"""
def close_door(window, direction, percentage, isAuto):
    global pct
    travel_distance = 0
    if percentage == 100:
        travel_distance = MIN_DOOR_CM
    else:  
        travel_distance = (MAX_DOOR_CM * (percentage/100)) + MIN_DOOR_CM
     
    last_distance = 0
    for _ in range(int(CHECK_COUNT*0.8)):
        for _ in range (CHECK_COUNT*4):
            distance = getSonar()
            last_distance = distance
            distance = getSonar()
            if distance == 0:
                distance = last_distance
            pct = 100 - int((MIN_DOOR_CM/distance)*100)
            if pct < 0:
                pct = 0

            if distance <= travel_distance:
                break
            moveSteps(direction, MOTOR_SPEED, MOTOR_STEPS)

    if not isAuto:
        window.write_event_value("closing_done", None)
    else:
        window.write_event_value("auto_reset_close", None)


"""
    cette methode permet d'ouvrir la porte selon un pourcentage et si c'est le mode est automatique ou non
"""
def open_door(window, direction, percentage, isAuto):
    global pct
    travel_distance = MAX_DOOR_CM * (percentage/100)

    for _ in range(int(CHECK_COUNT*0.8)):
        for _ in range (CHECK_COUNT*4):
            distance = getSonar()
            pct = int((distance/MAX_DOOR_CM) * 100)
            if pct > 100:
                pct = 100
            if distance >= travel_distance:
                break
            moveSteps(direction, MOTOR_SPEED, MOTOR_STEPS)
    
    if not isAuto:
        window.write_event_value("opening_done", None)
    else:
        window.write_event_value("auto_reset_open", None)



# =================== utilities ===================


# =================== functions ===================
"""
    cette methode defini les ports gpio
"""
def setup():
    print('Program is starting...')
    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)  # set trigPin to output mode
    GPIO.setup(echoPin, GPIO.IN)  # set echoPin to input mode
    for pin in motorPins:
        GPIO.setup(pin, GPIO.OUT)

"""
    cette methode est la boucle principal du programme et elle est affecter par les evenement de la boucle 
"""
def loop():
    window = user_interface()
    dht = DHT.DHT(DHTPin)  # create a DHT class object

    get_update = True
    isAutomatique = False

    closing_thread = None
    opening_thread = None

    counter = 0
    temperature = 0
    distance = 0
    temp_difference = 0

    temp_auto = 0
    last_temperature = 0
    temp_diff_auto = 0
    got_first = False

    while True:
        # mise a jour du poucentage et de la bar de progres
        window['-PROGRESS_BAR-'].update(pct)
        window['-STR_OPEN_DOOR_PCT-'].update(f"{str_door_open}{pct}%")
        
        # appel de methode qui permet de mettre a jour les elements a l'interface
        if get_update:
            update_thread = threading.Thread(target=get_updated_element, args = (window, 1), daemon = True)
            update_thread.start()
            get_update = False

        # si le mode automatique est activé
        if isAutomatique :
            temp_auto = getTemp(dht)

            # pour la premiere fois on monte la porte selon le pourcentage d'ouverture calculé
            if not got_first:
                last_temperature = temp_auto
                print("got first temp", last_temperature)
                temp_diff_auto = MAX_TEMP_READ - last_temperature
                percentage = 100 - int(temp_diff_auto * 10)

                print(last_temperature, "-", temp_auto, ": open")
                print("difference :", temp_diff_auto)
                print("percentage :", percentage)
                print("----------------------")

                opening_thread = threading.Thread(target=open_door, args = (window, DIRECTION_CW, percentage, True), daemon = True)
                opening_thread.start()
                isAutomatique = False
                got_first = True

            # pour si la temperature ne change pas, on fait rien
            if last_temperature == temp_auto:
                print("No change")
                print("----------------------")

            # pour si la temperature augemente, on fait monter la porte selon le pourcentage d'ouverture calculé
            if last_temperature < temp_auto:
                temp_diff_auto = MAX_TEMP_READ - last_temperature
                percentage = 100 - int(temp_diff_auto * 10)

                print(last_temperature, "-", temp_auto, ": open")
                print("difference :", temp_diff_auto)
                print("percentage :", percentage)
                print("----------------------")

                opening_thread = threading.Thread(target=open_door, args = (window, DIRECTION_CW, percentage, True), daemon = True)
                opening_thread.start()
                isAutomatique = False

            # pour si la temperature diminue, on fait descendre la porte selon le pourcentage d'ouverture calculé
            if last_temperature > temp_auto:
                temp_diff_auto = MAX_TEMP_READ - last_temperature
                percentage =  int(temp_diff_auto * 10)

                print(last_temperature, "-", temp_auto, ": close")
                print("difference :", temp_diff_auto)
                print("percentage :", percentage)
                print("----------------------")

                closing_thread = threading.Thread(target=close_door, args = (window, DIRECTION_CCW, 100-percentage, True), daemon = True)
                closing_thread.start()
                isAutomatique = False
            
            last_temperature = temp_auto

        
        # lecture d'evenement dans l'interface (timeout de 10 ms)
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break
        
        # si ce que l'utilisateur ecrit dans le champ de pourcentage n'est pas numerique on l'enleve
        if not check_number(values['-STR_INPUT_PCT-']):
            window['-STR_INPUT_PCT-'].update(values['-STR_INPUT_PCT-'][:-1])

        # si ce que l'utilisateur ecrit est numerique
        if check_number(values['-STR_INPUT_PCT-']):

            # on s'assure que ce n'est pas plus que 3 chiffres
            if len(values['-STR_INPUT_PCT-']) > 3:
                window['-STR_INPUT_PCT-'].update(values['-STR_INPUT_PCT-'][:-1])

            # on s'assure que c'est entre 1 a 100, si non on enleve
            if int(values['-STR_INPUT_PCT-']) > 100 or int(values['-STR_INPUT_PCT-']) < 0:
                window['-STR_INPUT_PCT-'].update(values['-STR_INPUT_PCT-'][:-len(values['-STR_INPUT_PCT-'])])
        
        # lorsque l'evenement de mise a jour les elements a l'interface est activé, on apporte le modifications
        if event == "can_update_element":
             counter += 1
             temperature = getTemp(dht)
             temp_difference = MAX_TEMP_READ - temperature
             distance = getSonar()

             print("Update count", counter)
             print("---------")
             print("Temperature: %.2f °C" % (temperature))
             print("Difference: %.2f °C" % (temp_difference))
             print("Distance: %.2f cm" % (distance))
             print("---------")

             window['-STR_TEMP-'].update("%.2f °C" % (temperature))
             get_update = True

        # evenements boutons, on applique les modifications selon le cas.
        if event == "AUTOMATIQUE_BTN":
            isAutomatique = True
            window['-OPEN_BTN-'].update(disabled=True)
            window['-CLOSE_BTN-'].update(disabled=True)

        if event == "MANUELLE_BTN":
            isAutomatique = False
            window['-OPEN_BTN-'].update(disabled=False)
            window['-CLOSE_BTN-'].update(disabled=False)

        if event == "-CLOSE_BTN-":
            if len(values['-STR_INPUT_PCT-']) > 1:
                window['-OPEN_BTN-'].update(disabled=True)
                percentage= float(values['-STR_INPUT_PCT-'])
                closing_thread = threading.Thread(target=close_door, args = (window, DIRECTION_CCW, 100 - percentage, False), daemon = True)
                closing_thread.start()


        if event == "-OPEN_BTN-":
            if len(values['-STR_INPUT_PCT-']) > 1:
                window['-CLOSE_BTN-'].update(disabled=True)
                percentage = float(values['-STR_INPUT_PCT-'])
                opening_thread = threading.Thread(target=open_door, args = (window, DIRECTION_CW, percentage, False), daemon = True)
                opening_thread.start()

        if event == "opening_done":
            window['-CLOSE_BTN-'].update(disabled=False)

        if event == "closing_done":
            window['-OPEN_BTN-'].update(disabled=False)

        if event == "auto_reset_close":
            isAutomatique = True

        if event == "auto_reset_open":
            isAutomatique = True

    window.close()


def destroy():
    GPIO.cleanup()

# =================== functions ===================

# =================== main ===================

if __name__ == '__main__':  
    # Program entrance
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()

# =================== main ===================
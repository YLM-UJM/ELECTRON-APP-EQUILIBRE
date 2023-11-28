from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from databaseHandler import databaseHandler
from computeParamEquilibre import computeParamEquilibre

import numpy as np
from time import sleep
import time
import websocket
import threading
import json
import pandas as pd
import beepy
from dotenv import load_dotenv
import os

load_dotenv()
# import paho.mqtt.client as mqtt

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')


# clientMQTT = mqtt.Client()
# clientMQTT.connect('localhost',1883)
detect = 0.60
masseDetected = 4
sideDetected = False
allowDetection = False
subjectOnPlateform = False
baseline = False
#SERIAL_NUMBER = 565882
SERIAL_NUMBER = 565863
# SERIAL_NUMBER = 584716
est_stable = 0
indice_stable = 0
essai = 0

config = 4
g = 9.81

if config == 4:
    order = [2,3,0,1]
if config == 3:
    order = [0,3,1,2]

print(order[0])

class StrainSensor():
    '''Class used to handle load cell type sensors. Extends Sensor class '''
    # Variables de classe pour stocker les données de tous les capteurs
    sensor_data = [pd.Series(dtype=float) for _ in range(4)]
    data_points_per_second = 62
    data_points_per_second_onPlateform = 250
    total = 0
    side = 'no one'
    total_L = 0
    total_R = 0
    baseline_L = 0
    baseline_R = 0
    


    def __init__(self,deviceSN,channelNo,dataInterval,A,B):
        '''
        Constructor for strain sensor phidgets. Takes standard Sensor arguments
        '''
        self.channelNo = channelNo
        self.sensorUnits = "Kg"
        self.A = A
        self.B = B
        self.deviceSN = deviceSN
        self.dataInterval = dataInterval
        self.accumulatedData = []
        self.offsetData = []
        self.offset = 0
        self.get = False
        self.getOffset = False
        self.offsetStartTime = 0
        self.side = 'no one'
        self.i = 0

    def attachSensor(self):
        '''
        Connects the strain sensor to the application
        '''
        self.channel = VoltageRatioInput()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(1000)
        self.attached = True
        self.channel.setDataInterval(self.dataInterval)
        self.channel.setBridgeGain(0x8)

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its utput values
        '''
        self.startTime = time.time()
        def onSensorValueChange(channelObject,voltageRatio):
            global i, baseline
            rawTime = time.time()
            deltaTime = rawTime- self.startTime
            if (config == 3):
                voltageRatio = ((voltageRatio-self.B) / self.A) 
            if (config == 4):
                voltageRatio = (((voltageRatio-self.B) / self.A)) / g
            
            voltageRatio = voltageRatio - self.offset
                        # Ajoutez la nouvelle valeur à la série de données du capteur
            StrainSensor.sensor_data[self.channelNo] = pd.concat([StrainSensor.sensor_data[self.channelNo], pd.Series([voltageRatio])], ignore_index=True)
            if (baseline):
                self.getBaseline()
            self.checkPosition()
            if sideDetected == False:
                self.checkSide()
            if self.getOffset:
                if time.time() - self.offsetStartTime <= 0.3:
                    self.offsetData.append(voltageRatio)
                else:
                    self.getOffset = False
            # if (self.channelNo == 2):
            #     print(self.channelNo,voltageRatio)
            # if self.i % 20 == 0:
            #     clientMQTT.publish(str(self.channelNo),voltageRatio)
            #     print(str(self.channelNo),voltageRatio)
                # if self.channelNo == 0:
                #     clientMQTT.publish(str(self.channelNo),voltageRatio)
                # if self.channelNo == 1:
                #     clientMQTT.publish(str(self.channelNo),voltageRatio)
                # if self.channelNo == 2:
                #     clientMQTT.publish(str(self.channelNo),voltageRatio)
                # if self.channelNo == 3:
                #     clientMQTT.publish(str(self.channelNo),voltageRatio)
            #data_point = [voltageRatio, deltaTime, rawTime]
            #self.dataQ.put([voltageRatio,deltaTime,rawTime])
            self.i += 1
            if self.get:
                self.accumulatedData.append(voltageRatio)
            #print(voltageRatio)
        self.channel.setOnVoltageRatioChangeHandler(onSensorValueChange)

    def setCallibration(self,gradient,intercept):
        self.gradient = gradient
        self.intercept = intercept

    def setOffset(self):
        self.getOffset = True
        self.offset = 0
        print('setOffset')
        self.offsetStartTime = time.time()
        # Attendre que la collecte de données soit terminée
        while self.getOffset:
            sleep(0.1)  # attendez un petit instant pour réduire la charge du CPU
        if (len(self.offsetData) > 0):
            self.offset = sum(self.offsetData) / len(self.offsetData)
        else:
            self.offset = 0
            print(self.offsetData)
            print(self.offsetStartTime)
        self.offsetData.clear()

    def checkPosition(self):
        global subjectOnPlateform, i
        StrainSensor.total = StrainSensor.sensor_data[0].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[3].iloc[-StrainSensor.data_points_per_second:].mean() + StrainSensor.sensor_data[1].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[2].iloc[-StrainSensor.data_points_per_second:].mean()
        if StrainSensor.total > masseDetected:
            i = i + 1
            if i >= 300:
                subjectOnPlateform = True
        else:
            i = 0
            subjectOnPlateform = False



    def checkSide(self):
        global sideDetected
        if allowDetection:
            if len(StrainSensor.sensor_data[self.channelNo]) >= StrainSensor.data_points_per_second:
                #print('detection en cours')
                if (StrainSensor.total > masseDetected):
                    if self.channelNo in [order[0], order[1]]:
                        StrainSensor.total_L = StrainSensor.sensor_data[order[0]].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[order[1]].iloc[-StrainSensor.data_points_per_second:].mean()

                    elif self.channelNo in [order[2], order[3]]:
                        # Utilisez pandas.concat au lieu de append
                        StrainSensor.total_R = StrainSensor.sensor_data[order[2]].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[order[3]].iloc[-StrainSensor.data_points_per_second:].mean()


                    #print(StrainSensor.total_L)
                    if (StrainSensor.total_L < (StrainSensor.baseline_L * detect) and StrainSensor.total_L != 0 and StrainSensor.baseline_L != 0 ):

                    #if (StrainSensor.total_L / StrainSensor.total) > detect:
                        self.side = 'right'
                        sideDetected = True
                        print('detected, pied gauche levé')
                        #print(StrainSensor.sensor_data)
                    elif (StrainSensor.total_R < (StrainSensor.baseline_R * detect) and StrainSensor.total_R != 0 and StrainSensor.baseline_R != 0  ):
                        self.side = 'left'
                        sideDetected = True
                        print('detected, pied droit levé')
                        #print(StrainSensor.sensor_data)
                    else:
                        self.side = 'both'
                else:
                    self.side = 'no one'
    
    def getBaseline(self):
        if self.channelNo in [order[0], order[1]]:
            StrainSensor.baseline_L = StrainSensor.sensor_data[order[0]].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[order[1]].iloc[-StrainSensor.data_points_per_second:].mean()


        if self.channelNo in [order[2], order[3]]:
            # Utilisez pandas.concat au lieu de append
            StrainSensor.baseline_R = StrainSensor.sensor_data[order[2]].iloc[-StrainSensor.data_points_per_second:].mean() +  StrainSensor.sensor_data[order[3]].iloc[-StrainSensor.data_points_per_second:].mean()




    def close(self):
        self.channel.close()
        print('Disconnected')

    def run(self):
        self.attachSensor()
        self.activateDataListener()
        print('run ok')

def toggle_data_recording(sensors, state):
    '''
    Active ou désactive l'enregistrement des données pour tous les capteurs
    sensors: Liste de capteurs
    state: True pour activer l'enregistrement, False pour le désactiver
    '''
    for sensor in sensors:
        sensor.get = state

def toggle_offset(sensors):
    for sensor in sensors:
        sensor.setOffset()


class WebSocketClient:
    def __init__(self, url, sensors, db):
        self.sensors = sensors
        self.db = db
        self.url = url
        self.ws = None
        self.reconnect_delay = 2  # temps d'attente avant de tenter de se reconnecter (en secondes)
        self.connected = False
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.idSession = None
        self.idUser = 0
        self.scoreLeft = 0
        self.scoreRight = 0


    def _run(self):
        while True:
            if not self.connected:
                try:
                    self.ws = websocket.WebSocketApp(self.url,
                                                        on_message=self.on_message,
                                                        on_error=self.on_error,
                                                        on_close=self.on_close)
                    self.ws.on_open = self.on_open
                    self.ws.run_forever()
                except Exception as e:
                    print(f"Connection failed. Retrying in {self.reconnect_delay} seconds. Error: {e}")
                    time.sleep(self.reconnect_delay)
            else:
                time.sleep(1)

    def on_error(self, ws, error):
        self.connected = False
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        print("Closed")

    def on_open(self, ws):
        self.connected = True
        print("Connected to the server")

    def on_message(self, ws, message):
        global sideDetected, allowDetection, subjectOnPlateform, i, essai, baseline
        #print(f"Received: {message}")
            # Vérifier si le message est non vide
        if message:
            try:
                # Essayez de charger le message en tant qu'objet JSON
                message_decode = json.loads(message)
                print('receive: ', message_decode, time.time())
                # if (int(message_decode['idUser']) > 0):
                #     self.idUser = int(message_decode['idUser'])
                print(self.idUser)
                # if (message_decode['status'] == 'offset'):
                #     toggle_offset(sensors)
                if (message_decode['status'] == 'newSession'):
                    self.idSession == None
                    payload = {
                        'topic': 'fromPython',
                        'status': 'newSession',
                    }

                    essai = 0
                    self.ws.send(json.dumps(payload))
                    
                elif (message_decode['status'] == 'wait' and message_decode['essai'] == 50 and subjectOnPlateform):
                    print('on')
                    baseline = message_decode['baseline']
                
                    if (baseline == False):
                        payload = {
                            'topic': 'fromPython',
                            'status': 'go',
                        }
                        self.ws.send(json.dumps(payload))



                elif (message_decode['status'] == 'start' and message_decode['essai'] == 100):
                    self.reset()
                    baseline = False
                    self.idUser = message_decode['idUser']
                    while subjectOnPlateform == False:
                        time.sleep(0.01)
                    payload = {
                        'topic': 'fromPython',
                        'status': 'onPlateform',
                    }
                    self.ws.send(json.dumps(payload))
                    print('on Plateforme')
                    self.idUser = message_decode['idUser']
                    # Créer une session si aucune existe
                    if (self.idSession == None):
                        self.idSession = self.db.createEquilibreSession(self.idUser)
                elif subjectOnPlateform and message_decode['essai'] <= 2:
                    self.reset()
                    if message_decode['essai'] == 0:
                        payload = {
                            'topic': 'fromPython',
                            'status': 'start',
                            'essai': 0
                        }
                        self.ws.send(json.dumps(payload))
                    ## Personne sur la plateforme
                    # self.ws.send(json.dumps(payload))
                    # INIT POUR ÊTRE SUR 
                    sideDetected = False
                    record_thread = threading.Thread(target=self.record_data)
                    record_thread.start()
                else:
                    payload = {
                        'topic': 'fromPython',
                        'status': 'no-one',
                    }
                    ## Personne sur la plateforme
                    self.ws.send(json.dumps(payload))
                if (message_decode['status'] == 'end'):
                    payload = {
                        'topic': 'fromPython',
                        'status': 'end'
                    }
                    self.ws.send(json.dumps(payload))
            except json.JSONDecodeError:
                # Si le message n'est pas un JSON valide, imprimez une erreur
                print(f"Impossible de décoder le message JSON: {message}")
        else:
            print("Message vide reçu.")
            message_decode = json.loads(message)
        #print(message_decode)
        # if (message_decode.status == '1'):
        #     # CHECK IF SOMEONE ON PLATEFORME
        #     if subjectOnPlateform:
        #         ## Personne sur la plateforme
        #         # self.ws.send(json.dumps(payload))
        #         # INIT POUR ÊTRE SUR 
        #         sideDetected = False
        #         allowDetection= True
        #         # Créer une session si aucune existe
        #         if (self.idSession == None):
        #             self.idSession = self.db.createEquilibreSession()
        #         record_thread = threading.Thread(target=self.record_data)
        #         record_thread.start()
        #     else:
        #         payload = {
        #             'status': 'no-one'
        #         }
        #         ## Personne sur la plateforme
        #         self.ws.send(json.dumps(payload))
        #         print('personne sur la plateforme')
        # if (message == '100'):
        #     toggle_offset(sensors)

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Closed")

    def on_open(self, ws):
        print("Connected to the server")

    def close(self):
        self.ws.close()
        self.thread.join()

    def record_data(self):
        global sideDetected, allowDetection, essai
        count = self.db.config.durationStability
        print('record_data')
        receiveTime = time.time()
        allowDetection= True
        time.sleep(0.2)
        while sideDetected == False:
            time.sleep(0.01)
            if time.time() - receiveTime >= self.db.config.delayDetection:
                break
        if sideDetected:
            essai += 1
            toggle_data_recording(sensors, True)
            payload = {
                'topic': 'fromPython',
                'status': 'detect ok',
                'decompte': count
            }
            self.ws.send(json.dumps(payload))
            allowDetection = False
            startTime = time.time()
            while time.time() - startTime < self.db.config.durationStability:
                sleep(1)
                print(count)
                count -= 1
                payload = {
                    'topic': 'fromPython',
                    'status': 'on-running',
                    'decompte': count
                }
                self.ws.send(json.dumps(payload))
            # levé de pied detecté
            # Désactivez l'enregistrement
            toggle_data_recording(sensors, False)
            beepy.beep(sound=1)
            # Créez un objet JSON avec les données accumulées
            #print(len(S0.accumulatedData))
            data = {
                'sensor0': S0.accumulatedData,
                'sensor1': S1.accumulatedData,
                'sensor2': S2.accumulatedData,
                'sensor3': S3.accumulatedData
            }
            json_data = json.dumps(data)
            equilibre = computeParamEquilibre()
            equilibre.set_data_from_json(data)
            EA = equilibre.computeAcquisition(self.idSession,self.db)
            # Envoyez les données à Electron
            if essai == 2:

                results = self.db.getResults(self.idSession)
                print(results)
                payload = {
                    'topic': 'fromPython',
                    'status': 'result',
                    'scoreL': results[0],
                    'scoreR': results[1]
                }
                self.ws.send(json.dumps(payload))
                essai = 0
                results = None
            
            toggle_data_recording(sensors, False)
        else:
            #aucune detection du pied 
            print('aucune detection')
            allowDetection = False
            payload = {
                'topic': 'fromPython',
                'status': 'no-detect'
            }
            self.ws.send(json.dumps(payload))
            toggle_data_recording(sensors, False)

    def reset(self):
        global sideDetected
        S0.accumulatedData = []
        S1.accumulatedData = []
        S2.accumulatedData = []
        S3.accumulatedData = []

        for i in range(len(StrainSensor.sensor_data)):
            StrainSensor.sensor_data[i] = pd.Series(dtype=float)
        StrainSensor.total_L = 0
        StrainSensor.total_R = 0
        sideDetected = False


    
if __name__ == '__main__':
    db = databaseHandler(DB_HOST,DB_USER,DB_PASSWORD,DB_NAME,DB_PORT,config)
    S0 = StrainSensor(SERIAL_NUMBER,0,db.config.dataIntervalStability,db.config.A0,db.config.B0)
    S1 = StrainSensor(SERIAL_NUMBER,1,db.config.dataIntervalStability,db.config.A1,db.config.B1)
    S2 = StrainSensor(SERIAL_NUMBER,2,db.config.dataIntervalStability,db.config.A2,db.config.B2)
    S3 = StrainSensor(SERIAL_NUMBER,3,db.config.dataIntervalStability,db.config.A3,db.config.B3)
    S0.run()
    S1.run()
    S2.run()
    S3.run()


    # Liste de tous les capteurs
    sensors = [S0, S1, S2, S3]
    toggle_offset(sensors)

    client = WebSocketClient("ws://localhost:8080",sensors,db)

    # Attendre que l'utilisateur appuie sur Enter
    print("Press ENTER to terminate...")
    input()  # Attend jusqu'à ce que l'utilisateur appuie sur Enter
    
    S0.close()
    S1.close()
    S2.close()
    S3.close()
    client.close()

    
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *

import numpy as np
from time import sleep
import time
import websocket
import threading
import json


class StrainSensor():
    '''Class used to handle load cell type sensors. Extends Sensor class '''

    def __init__(self,deviceSN,channelNo,dataInterval, sensorName):
        '''
        Constructor for strain sensor phidgets. Takes standard Sensor arguments
        '''
        self.channelNo = channelNo
        self.sensorUnits = "Kg"
        self.useCallibration = False
        self.gradient = 1
        self.intercept = 0
        self.deviceSN = deviceSN
        self.dataInterval = dataInterval
        self.sensorName = sensorName
        self.accumulatedData = []
        self.get = False

    def attachSensor(self):
        '''
        Connects the strain sensor to the application
        '''
        self.channel = VoltageRatioInput()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(1000)
        print("\n***** {} Sensor Attached *****".format(self.sensorName))
        self.attached = True
        self.channel.setDataInterval(self.dataInterval)
        self.channel.setBridgeGain(0x8)

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its utput values
        '''
        self.startTime = time.time()
        def onSensorValueChange(channelObject,voltageRatio):
            rawTime = time.time()
            deltaTime = rawTime- self.startTime
            if self.useCallibration:
                voltageRatio = voltageRatio*self.gradient + self.intercept
            #data_point = [voltageRatio, deltaTime, rawTime]
            #self.dataQ.put([voltageRatio,deltaTime,rawTime])
            if self.get:
                self.accumulatedData.append(voltageRatio)
            #print(voltageRatio)
        self.channel.setOnVoltageRatioChangeHandler(onSensorValueChange)

    def setCallibration(self,gradient,intercept):
        '''
        Used to give the sensor callibration values.
        '''
        self.gradient = gradient
        self.intercept = intercept
        self.useCallibration = True

    def close(self):
        self.channel.close()
        print('Disconnected')

    def run(self):
        self.attachSensor()
        self.activateDataListener()

def toggle_data_recording(sensors, state):
    '''
    Active ou désactive l'enregistrement des données pour tous les capteurs
    sensors: Liste de capteurs
    state: True pour activer l'enregistrement, False pour le désactiver
    '''
    for sensor in sensors:
        sensor.get = state

class WebSocketClient:
    def __init__(self, url, sensors):
        self.sensors = sensors
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        self.ws.run_forever()

    def on_message(self, ws, message):
        print(f"Received: {message}")
        record_thread = threading.Thread(target=self.record_data)
        record_thread.start()

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
        # Activez l'enregistrement pour tous les capteurs
        toggle_data_recording(sensors, True)
        
        # Enregistrez pendant 2 secondes
        sleep(2)
        
        # Désactivez l'enregistrement
        toggle_data_recording(sensors, False)
        
        # Créez un objet JSON avec les données accumulées
        data = {
            'sensor0': S1.accumulatedData,
            'sensor1': S2.accumulatedData
        }
        json_data = json.dumps(data)
        
        # Envoyez les données à Electron
        self.ws.send(json_data)
    
if __name__ == '__main__':
    S1 = StrainSensor(565882,0,80,'sensor 0')
    S2 = StrainSensor(565882,1,80,'sensor 1')
    S1.run()
    S2.run()

    # Liste de tous les capteurs
    sensors = [S1, S2]

    client = WebSocketClient("ws://localhost:8080", sensors)

    # Attendre que l'utilisateur appuie sur Enter
    print("Press ENTER to terminate...")
    input()  # Attend jusqu'à ce que l'utilisateur appuie sur Enter
    
    S1.close()
    S2.close()
    client.close()

    
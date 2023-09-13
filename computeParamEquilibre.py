from numpy import linalg as LA
from scipy import signal
import numpy as np
import time
from datetime import datetime
import math  # Je l'ai ajouté car vous utilisez round et math.pi

class computeParamEquilibre():

    def __init__(self):
        self.data = {}
        self.inputX = []
        self.inputY = []
        self.encodeur = []

    def set_data_from_json(self, json_data):
        self.data = json_data

    def computeAcquisition(self, idSession,db):
        voltagesMin = min(len(self.data['sensor0']), len(self.data['sensor1']), 
                          len(self.data['sensor2']), len(self.data['sensor3']))
        for i in range(voltagesMin):
            self.inputX.append(0 - self.data['sensor1'][i] - self.data['sensor2'][i] + 
                               self.data['sensor0'][i] + self.data['sensor3'][i])
            self.inputY.append(0 - self.data['sensor2'][i] - self.data['sensor3'][i] + 
                               self.data['sensor1'][i] + self.data['sensor0'][i])
            self.encodeur.append([self.data['sensor0'][i], self.data['sensor1'][i], 
                                  self.data['sensor2'][i], self.data['sensor3'][i]])
        npArrayEncodeur = np.array(self.encodeur)
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y__%H:%M:%S")
        #np.savetxt(dt_string + ".csv", npArrayEncodeur, delimiter=',', fmt='%f')
        fs = 1000 / 16
        fc = 20
        w = fc / (fs / 2)
        b, a = signal.butter(4, w, "low")
        outputX = signal.filtfilt(b, a, self.inputX)
        outputY = signal.filtfilt(b, a, self.inputY)
        vec, val = LA.eig(np.cov(outputX, outputY))
        EA = round(math.pi * np.prod(2.4478 * np.sqrt(vec)), 2)
        db.insertResults(idSession,EA)
        print(EA)
        #calculate_cop(self,0.50,0.35)
        return EA
    
    import numpy as np

def calculate_cop(self, L, W):
    """
    Calcule les coordonnées CoP à partir des mesures des capteurs de force.
    
    Paramètres:
    - force_sensors : tableau numpy (n, 4) contenant les mesures des capteurs de force (F1, F2, F3, F4) pour n échantillons.
    - L, W : longueur et largeur de la plateforme de force.

    Renvoie:
    - cop_x, cop_y : coordonnées x et y du CoP.
    """

    F_total = np.sum(self.data, axis=1)

    cop_x = ((self.data['sensor0'] + self.data['sensor1']) - (self.data['sensor2'] + self.data['sensor3'])) * L / (2 * F_total)
    #cop_y = ((force_sensors[:, 0] + force_sensors[:, 2]) - (force_sensors[:, 1] + force_sensors[:, 3])) * W / (2 * F_total)
    print(cop_x)
    #return cop_x, cop_y




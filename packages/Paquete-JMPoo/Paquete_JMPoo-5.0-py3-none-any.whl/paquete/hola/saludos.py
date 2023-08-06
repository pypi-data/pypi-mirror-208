import numpy as np

def saludar():
    print("hola saludos, te saludo desde el modulo saludos.saludar()")

def generar_array(numeros):
    return np.arange(numeros)


class Saludo:
    def __init__(self):
        print("hola, te estoy saludando desde la clase Saludo.__init__")
        
if __name__ =='__main__':
    print(generar_array(5))
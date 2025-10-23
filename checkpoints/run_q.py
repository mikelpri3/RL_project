import pickle

ruta_archivo = 'checkpoints/best_q.pkl'

with open(ruta_archivo, 'rb') as archivo:
    datos = pickle.load(archivo)

print(datos)
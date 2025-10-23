import pickle

ruta_archivo = 'checkpoints/best_sarsa_agent.pkl'

with open(ruta_archivo, 'rb') as archivo:
    datos = pickle.load(archivo)

print(datos)
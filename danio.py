# Importamos el DataFrame desde nuestro archivo data.py
from data import df_tipos
import pandas as pd # Lo necesitamos por si un tipo es nulo (NaN)
import random

def calcular_efectividad(tipo_atacante, tipo_defensor):
    """
    Calcula la efectividad de un tipo de ataque contra un tipo de defensor
    utilizando el DataFrame de la tabla de tipos.
    """
    # Si el pokemon defensor no tiene segundo tipo, este será nulo (NaN).
    # En ese caso, la efectividad es neutra (1).
    if pd.isna(tipo_defensor):
        return 1
    
    # Usamos .loc para buscar en el DataFrame por índice (atacante) y columna (defensor)
    # y así obtener el multiplicador de daño.
    try:
        efectividad = df_tipos.loc[tipo_atacante, tipo_defensor]
        return efectividad
    except KeyError:
        # Si algún tipo no se encuentra en la tabla, devolvemos 1 como valor por defecto.
        print(f"Advertencia: El tipo '{tipo_atacante}' o '{tipo_defensor}' no fue encontrado. Se usará efectividad neutra.")
        return 1



def same_type_attack_bonus(tipo_pokemon1, tipo_pokemon2, tipo_mov):
    """
    Aplica el multiplicador STAB (Same-Type Attack Bonus) si el tipo del movimiento
    coincide con alguno de los tipos del Pokémon atacante.
    """
    multiplicador = 1.0
    # Un Pokémon recibe STAB si el movimiento es de su tipo1 O de su tipo2
    if tipo_pokemon1 == tipo_mov or tipo_pokemon2 == tipo_mov:
        multiplicador = 1.5

    return multiplicador


def calcular_danio(pokemon_atacante, pokemon_defensor, mov):
    """
    Calcula el daño final de un movimiento.
    Asume que los objetos pokemon y mov tienen los atributos necesarios.
    """
    danio = 0
    precision_random = random.randint(1, 100)

    # Corregido: mov.precision es el nombre correcto del atributo
    if mov.precision < precision_random:
        danio = 0
        print("El ataque ha fallado!")
        return danio
        
    # La efectividad total es el producto de las efectividades contra cada tipo.
    # Corregido: mov.tipo -> mov.type
    efectividad1 = calcular_efectividad(mov.type, pokemon_defensor.type1)
    efectividad2 = calcular_efectividad(mov.type, pokemon_defensor.type2)
    efectividad_total = efectividad1 * efectividad2

    if efectividad_total == 2:
        print("Es superefectivo!!")
    if efectividad_total == 4:
        print("Es megaefectivo!!")
    if efectividad_total == 0.5:
        print("Es poco efectivo...")
    if efectividad_total == 0.25:   
        print("Es muy poco efectivo...")
    if efectividad_total == 0:
        print("El pokemon rival es inmune...")
    
    # El multiplicador por ser del mismo tipo (STAB)
    # Corregido: mov.tipo -> mov.type
    multiplicador_stab = same_type_attack_bonus(pokemon_atacante.type1, pokemon_atacante.type2, mov.type)

    # Fórmula de daño simplificada
    if mov.special: # mov.special ya es un booleano, no necesitas '== 1'
        # Corregido: atributos de daño y stats en inglés
        danio = mov.damage * efectividad_total * multiplicador_stab * (pokemon_atacante.sp_atk / pokemon_defensor.sp_def) * 0.2
    else: # Si es un ataque físico
        # Corregido: atributos de daño y stats en inglés
        danio = mov.damage * efectividad_total * multiplicador_stab * (pokemon_atacante.attack / pokemon_defensor.defense) * 0.2

    return danio


def ko(danio, vida):
    """
    Comprueba si el daño es suficiente para dejar fuera de combate (KO).
    """
    return danio >= vida



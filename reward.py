# reward.py

# Importamos la función de cálculo de efectividad para no reescribir código
from danio import calcular_efectividad

def calcular_reward_turno(
    danio_hecho: float,
    danio_recibido: float,
    pokemon_jugador,
    pokemon_oponente,
    movimiento_jugador,
    movimiento_oponente
) -> float:
    """
    Calcula la recompensa para el jugador basándose en el resultado del turno.

    La fórmula es:
    (%daño hecho - %daño recibido) * efectividad_ofensiva / efectividad_defensiva
    """
    
    # 1. Calcular el daño como porcentaje de la vida máxima
    # Se evita dividir por cero si un Pokémon tiene 0 HP (aunque no debería pasar)
    porc_danio_hecho = (danio_hecho / pokemon_oponente.hp) if pokemon_oponente.hp > 0 else 1
    porc_danio_recibido = (danio_recibido / pokemon_jugador.hp)  if pokemon_jugador.hp > 0 else 1

    # 2. Calcular la efectividad del ataque del jugador
    efectividad_ofensiva = (
        calcular_efectividad(movimiento_jugador.type, pokemon_oponente.type1) *
        calcular_efectividad(movimiento_jugador.type, pokemon_oponente.type2)
    )

    # 3. Calcular la efectividad del ataque del oponente
    efectividad_defensiva = (
        calcular_efectividad(movimiento_oponente.type, pokemon_jugador.type1) *
        calcular_efectividad(movimiento_oponente.type, pokemon_jugador.type2)
    )
    
    # 4. Evitar la división por cero si el ataque del oponente era inmune
    # Si el ataque rival es inmune (efectividad 0), es muy bueno para nosotros,
    # por lo que usamos un divisor pequeño para que la recompensa sea alta.
    if efectividad_defensiva == 0:
        efectividad_defensiva = 0.01 # Equivalente a "muy muy poco efectivo"

    # 5. Aplicar la fórmula final
    diferencial_danio = porc_danio_hecho - porc_danio_recibido
    modificador_efectividad = efectividad_ofensiva / efectividad_defensiva
    
    reward = diferencial_danio + modificador_efectividad - 1
    
    return reward
# reward.py

from danio import calcular_efectividad

def _calcular_mejor_efectividad_posible(pokemon_jugador, pokemon_oponente):
    """
    Calcula la máxima efectividad que el Pokémon del jugador podría alcanzar
    contra el oponente actual usando cualquiera de sus movimientos.
    """
    if not pokemon_jugador.movimientos: return 0
    mejor_efectividad = 0
    for mov in pokemon_jugador.movimientos:
        efectividad_actual = (
            calcular_efectividad(mov.type, pokemon_oponente.type1) *
            calcular_efectividad(mov.type, pokemon_oponente.type2)
        )
        if efectividad_actual > mejor_efectividad:
            mejor_efectividad = efectividad_actual
    return mejor_efectividad

def calcular_reward_turno(
    danio_hecho: float,
    danio_recibido: float,
    pokemon_jugador,
    pokemon_oponente,
    movimiento_jugador,
    movimiento_oponente,
    oponente_pre_cambio=None,
    # <<< NUEVOS PARÁMETROS >>>
    vida_oponente_antes_ko=None,
    vida_jugador_antes_ko=None
) -> float:
    """
    Calcula la recompensa para el jugador basándose en el resultado del turno.
    """
    oponente_real_del_turno = oponente_pre_cambio if oponente_pre_cambio else pokemon_oponente
    
    # <<< LÓGICA DE CÁLCULO DE DAÑO PORCENTUAL ACTUALIZADA >>>
    if vida_oponente_antes_ko is not None:
        # Si hubo un KO ofensivo, el "daño" es 1 (por el KO) + el % de vida que le quedaba.
        porc_danio_hecho = 1.0 + (vida_oponente_antes_ko / oponente_real_del_turno.hp)
    else:
        # Cálculo normal si no hubo KO.
        porc_danio_hecho = (danio_hecho / oponente_real_del_turno.hp) if oponente_real_del_turno.hp > 0 else 0

    if vida_jugador_antes_ko is not None:
        # Si hubo un KO defensivo, el "daño" es 1 (por el KO) + el % de vida que te quedaba.
        porc_danio_recibido = 1.0 + (vida_jugador_antes_ko / pokemon_jugador.hp)
    else:
        # Cálculo normal si no hubo KO.
        porc_danio_recibido = (danio_recibido / pokemon_jugador.hp) if pokemon_jugador.hp > 0 else 0

    # Lógica de efectividad ofensiva (sin cambios)
    if movimiento_jugador.name == "Cambio":
        efectividad_ofensiva = _calcular_mejor_efectividad_posible(pokemon_jugador, oponente_real_del_turno)
    else:
        efectividad_ofensiva = (
            calcular_efectividad(movimiento_jugador.type, oponente_real_del_turno.type1) *
            calcular_efectividad(movimiento_jugador.type, oponente_real_del_turno.type2)
        )

    # Lógica de efectividad defensiva (sin cambios)
    efectividad_defensiva = (
        calcular_efectividad(movimiento_oponente.type, pokemon_jugador.type1) *
        calcular_efectividad(movimiento_oponente.type, pokemon_jugador.type2)
    )
    
    if efectividad_defensiva == 0:
        efectividad_defensiva = 0.01

    # Fórmula final (sin cambios)
    diferencial_danio = porc_danio_hecho - porc_danio_recibido
    modificador_efectividad = efectividad_ofensiva / efectividad_defensiva
    reward = diferencial_danio + modificador_efectividad - 1
    
    return reward
def calcular_efectividad(tipoAtacante, tipoDefensor):
    efectividad = 0
    if tipoAtacante == "Fuego":
        if tipoDefensor == "Fuego":
            efectividad = 0.5
            return efectividad
        if tipoDefensor == "Planta":
            efectividad = 2
            return efectividad 
        if tipoDefensor == "Agua":
            efectividad == 0.5
            return efectividad
        
    elif tipoAtacante == "Agua":
        if tipoDefensor == "Fuego":
            efectividad = 2
            return efectividad
        if tipoDefensor == "Planta":
            efectividad = 0.5
            return efectividad 
        if tipoDefensor == "Agua":
            efectividad == 0.5
            return efectividad
        
    elif tipoAtacante == "Planta":
        if tipoDefensor == "Fuego":
            efectividad = 0.5
            return efectividad
        if tipoDefensor == "Planta":
            efectividad = 0.5
            return efectividad 
        if tipoDefensor == "Agua":
            efectividad == 2
            return efectividad
        
    else:
        efectividad == 1
        return efectividad
    

def same_type(tipo_pokemon, tipo_mov):
    multiplicador = 1
    if tipo_pokemon == tipo_mov:
        multiplicador = 1.5

    return multiplicador


def calcular_danio(pokemon_atacante, pokemon_defensor, mov):
    danio = 0

    efectividad = calcular_efectividad(mov.tipo, pokemon_defensor.tipo)
    multiplicador = same_type(pokemon_atacante.tipo, mov.tipo)

    if mov.special == 1:
        danio = mov.danio * efectividad * multiplicador * pokemon_atacante.ataque_especial / pokemon_defensor.defensa_especial

    else: 
        danio = mov.danio * efectividad * multiplicador * pokemon_atacante.ataque_fisica / pokemon_defensor.defensa_fisica

    return danio


def ko(danio, vida):
    if danio > vida:
        return True
    else:
        return False
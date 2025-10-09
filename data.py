import pandas as pd
from typing import List, Dict, Optional

# Se asume que el archivo 'classes.py' está en el mismo directorio
from classes import Movimiento, Pokemon, Entrenador

# --- DEFINICIÓN GLOBAL DE LA TABLA DE EFECTIVIDADES ---

tipos = [
    "Normal", "Fuego", "Agua", "Planta", "Electrico", "Hielo", "Lucha", "Veneno", "Tierra",
    "Volador", "Psiquico", "Bicho", "Roca", "Fantasma", "Dragon", "Siniestro", "Acero", "Hada"
]

datos_efectividad = [
    # Defensor ->
    # Nor   Fue    Agu    Pla    Elé    Hie    Luc    Ven    Tie    Vol    Psi    Bic    Roc    Fan    Dra    Sin    Ace    Had   ↓ Atacante
    [1.0,  1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   0.5,   0.0,   1.0,   1.0,   0.5,   1.0], # Normal
    [1.0,  0.5,   0.5,   2.0,   1.0,   2.0,   1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   0.5,   1.0,   0.5,   1.0,   2.0,   1.0], # Fuego
    [1.0,  2.0,   0.5,   0.5,   1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   1.0,   1.0,   2.0,   1.0,   0.5,   1.0,   1.0,   1.0], # Agua
    [1.0,  0.5,   2.0,   0.5,   1.0,   1.0,   1.0,   0.5,   2.0,   0.5,   1.0,   0.5,   2.0,   1.0,   0.5,   1.0,   0.5,   1.0], # Planta
    [1.0,  1.0,   2.0,   0.5,   0.5,   1.0,   1.0,   1.0,   0.0,   2.0,   1.0,   1.0,   1.0,   1.0,   0.5,   1.0,   1.0,   1.0], # Eléctrico
    [1.0,  0.5,   0.5,   2.0,   1.0,   0.5,   1.0,   1.0,   2.0,   2.0,   1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   0.5,   1.0], # Hielo
    [2.0,  1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   0.5,   1.0,   0.5,   0.5,   0.5,   2.0,   0.0,   1.0,   2.0,   2.0,   0.5], # Lucha
    [1.0,  1.0,   1.0,   2.0,   1.0,   1.0,   1.0,   0.5,   0.5,   1.0,   1.0,   1.0,   0.5,   0.5,   1.0,   1.0,   0.0,   2.0], # Veneno
    [1.0,  2.0,   1.0,   0.5,   2.0,   1.0,   1.0,   2.0,   1.0,   0.0,   1.0,   0.5,   2.0,   1.0,   1.0,   1.0,   2.0,   1.0], # Tierra
    [1.0,  1.0,   1.0,   2.0,   0.5,   1.0,   2.0,   1.0,   1.0,   1.0,   1.0,   2.0,   0.5,   1.0,   1.0,   1.0,   0.5,   1.0], # Volador
    [1.0,  1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   2.0,   1.0,   1.0,   0.5,   1.0,   1.0,   1.0,   1.0,   0.0,   0.5,   1.0], # Psíquico
    [1.0,  0.5,   1.0,   2.0,   1.0,   1.0,   0.5,   0.5,   1.0,   0.5,   2.0,   1.0,   1.0,   0.5,   1.0,   2.0,   0.5,   0.5], # Bicho
    [1.0,  2.0,   1.0,   1.0,   1.0,   2.0,   0.5,   1.0,   0.5,   2.0,   1.0,   2.0,   1.0,   1.0,   1.0,   1.0,   0.5,   1.0], # Roca
    [0.0,  1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   1.0,   2.0,   1.0,   0.5,   1.0,   1.0], # Fantasma
    [1.0,  1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   0.5,   0.0], # Dragón
    [1.0,  1.0,   1.0,   1.0,   1.0,   1.0,   0.5,   1.0,   1.0,   1.0,   2.0,   1.0,   1.0,   2.0,   1.0,   0.5,   1.0,   0.5], # Siniestro
    [1.0,  0.5,   0.5,   1.0,   0.5,   2.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   1.0,   1.0,   1.0,   0.5,   2.0], # Acero
    [1.0,  0.5,   1.0,   1.0,   1.0,   1.0,   2.0,   0.5,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   2.0,   2.0,   0.5,   1.0]  # Hada
]
df_tipos = pd.DataFrame(data=datos_efectividad, index=tipos, columns=tipos)


# --- FUNCIONES PARA CREAR OBJETOS ---

def generar_csv_limpio():
    """
    Lee 'pokemon.csv', lo limpia y guarda el resultado en 'pokemon_limpio.csv'.
    Esta es la única función responsable de esta tarea.
    """
    df = pd.read_csv('assets/csv/pokemon.csv')
    traduccion_tipos = {
        'Grass': 'Planta', 'Fire': 'Fuego', 'Water': 'Agua', 'Bug': 'Bicho',
        'Normal': 'Normal', 'Poison': 'Veneno', 'Electric': 'Electrico',
        'Ground': 'Tierra', 'Fairy': 'Hada', 'Fighting': 'Lucha',
        'Psychic': 'Psiquico', 'Rock': 'Roca', 'Ghost': 'Fantasma',
        'Ice': 'Hielo', 'Dragon': 'Dragon', 'Dark': 'Siniestro',
        'Steel': 'Acero', 'Flying': 'Volador'
    }
    
    # Filtros combinados con regex para más eficiencia
    df_limpio = df[~df['Name'].str.contains('Mega', na=False) | df['Name'].isin(['Meganium', 'Yanmega'])]
    df_limpio = df_limpio[~df_limpio['Name'].str.contains('Size|Primal|Forme|Mode|Cloak|Rotom|Unbound|Black|White', na=False, regex=True)]

    df_limpio = df_limpio[['#', 'Name', 'Type 1', 'Type 2', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']]
    df_limpio.columns = ['id', 'name', 'type1', 'type2', 'HP', 'Attack', 'Defense', 'Sp.Atk', 'Sp.Def', 'Speed']

    df_limpio['type1'] = df_limpio['type1'].map(traduccion_tipos)
    df_limpio['type2'] = df_limpio['type2'].map(traduccion_tipos)

    df_limpio.to_csv('assets/csv/pokemon_limpio.csv', index=False)
    print("Archivo 'pokemon_limpio.csv' generado/actualizado exitosamente.")
    return df_limpio


def crear_todos_los_movimientos() -> Dict[str, Movimiento]:
    """
    Lee 'movs.csv' y crea un diccionario de objetos Movimiento.
    """
    df_movs = pd.read_csv('assets/csv/movs.csv')
    df_movs.columns = [col.strip() for col in df_movs.columns]
    
    diccionario_movimientos = {}
    for _, row in df_movs.iterrows():
        movimiento = Movimiento(
            id=row['ID'],
            name=row['Name'].strip(),
            type=row['Type'].strip(),
            special=bool(row['Special']),
            damage=row['Damage'],
            precision=row['Precision']
        )
        diccionario_movimientos[movimiento.name] = movimiento
        
    return diccionario_movimientos


def crear_todos_los_pokemon() -> List[Pokemon]:
    """
    Crea una lista de objetos Pokémon, combinando estadísticas y movimientos.
    """
    try:
        df_pokemon_stats = pd.read_csv('assets/csv/pokemon_limpio.csv')
    except FileNotFoundError:
        print("El archivo 'pokemon_limpio.csv' no existe. Generándolo ahora...")
        df_pokemon_stats = generar_csv_limpio()

    movimientos_disponibles = crear_todos_los_movimientos()
    df_pokemon_movs = pd.read_csv('assets/csv/pokemon_movs.csv')
    df_pokemon_movs.columns = [col.strip() for col in df_pokemon_movs.columns]
    df_pokemon_movs.set_index('NamePokemon', inplace=True)

    lista_pokemon_creados = []
    for _, row in df_pokemon_stats.iterrows():
        pokemon_name = row['name']

        if pokemon_name not in df_pokemon_movs.index:
            continue
        
        pokemon_actual = Pokemon(
            id=row['id'],
            name=pokemon_name,
            type1=row['type1'],
            type2=row['type2'] if pd.notna(row['type2']) else None,
            hp=row['HP'],
            attack=row['Attack'],
            defense=row['Defense'],
            sp_atk=row['Sp.Atk'],
            sp_def=row['Sp.Def'],
            speed=row['Speed'],
            imagen=f"assets/images/pokemon_images/{pokemon_name}.png"
        )

        nombres_movs = df_pokemon_movs.loc[pokemon_name]
        movimientos_asignados = [
            movimientos_disponibles.get(move_name.strip()) 
            for move_name in nombres_movs 
            if pd.notna(move_name) and movimientos_disponibles.get(move_name.strip())
        ]

        pokemon_actual.asignar_movimientos(movimientos_asignados)
        lista_pokemon_creados.append(pokemon_actual)

    return lista_pokemon_creados



def crear_todos_los_entrenadores() -> List[Entrenador]:
    """
    Crea una lista de objetos Entrenador a partir del CSV, asignándoles
    sus respectivos equipos de Pokémon.

    Returns:
        List[Entrenador]: Una lista con todas las instancias de la clase Entrenador.
    """
    # 1. Necesitamos todos los objetos Pokémon disponibles para poder asignarlos.
    #    Los convertimos a un diccionario para una búsqueda por nombre súper rápida.
    lista_pokemon_disponibles = crear_todos_los_pokemon()
    pokemon_lookup = {pokemon.name: pokemon for pokemon in lista_pokemon_disponibles}

    # 2. Leemos el archivo CSV de los entrenadores.
    df_trainers = pd.read_csv('assets/csv/trainer_pokemon.csv')
    df_trainers.columns = [col.strip() for col in df_trainers.columns]

    lista_entrenadores_creados = []
    entrenador_id_counter = 1 # Para el ID autoincremental

    # 3. Iteramos sobre cada fila para crear un entrenador.
    for _, row in df_trainers.iterrows():
        trainer_name = row['TrainerName'].strip()

        # 4. Creamos la instancia base del Entrenador.
        entrenador_actual = Entrenador(
            id=entrenador_id_counter,
            name=trainer_name,
            imagen=f"assets/images/trainer_images/{trainer_name}.png"
        )
        
        # 5. Buscamos los Pokémon de su equipo en nuestro diccionario.
        equipo_pokemon = []
        nombres_pokemon_equipo = [row['Pokemon1'], row['Pokemon2'], row['Pokemon3']]
        
        for nombre_poke in nombres_pokemon_equipo:
            if pd.notna(nombre_poke):
                # Usamos .get() para buscar el objeto Pokémon por su nombre
                pokemon_obj = pokemon_lookup.get(nombre_poke.strip())
                if pokemon_obj:
                    equipo_pokemon.append(pokemon_obj)

        # 6. Asignamos el equipo al entrenador y lo añadimos a la lista.
        entrenador_actual.asignar_equipo(equipo_pokemon)
        lista_entrenadores_creados.append(entrenador_actual)
        
        entrenador_id_counter += 1 # Incrementamos el ID para el siguiente

    return lista_entrenadores_creados
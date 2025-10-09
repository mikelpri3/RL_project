from typing import List, Optional

class Movimiento:
    """
    Representa un movimiento (ataque) que un Pokémon puede aprender.
    """
    def __init__(self, id: int, name: str, type: str, special: bool, damage: int, precision: int):
        """
        Inicializa una nueva instancia de Movimiento.

        Args:
            id (int): El identificador único para el movimiento.
            name (str): El nombre del movimiento (ej: "Lanzallamas").
            type (str): El tipo del movimiento (ej: "Fuego").
            special (bool): True si es un ataque especial, False si es físico.
            damage (int): El poder base del movimiento.
            precision (int): La precisión del movimiento (de 0 a 100).
        """
        self.id = id
        self.name = name
        self.type = type
        self.special = special
        self.damage = damage
        self.precision = precision

    def __repr__(self):
        """Devuelve una representación en string del objeto para facilitar la depuración."""
        return (f"Movimiento(id={self.id}, name='{self.name}', type='{self.type}', "
                f"damage={self.damage})")


class Pokemon:
    """
    Representa a una criatura Pokémon con sus estadísticas, tipos y movimientos.
    """
    def __init__(self, id: int, name: str, type1: str, type2: Optional[str], hp: int, 
                 attack: int, defense: int, sp_atk: int, sp_def: int, speed: int, imagen: str):
        """
        Inicializa una nueva instancia de Pokémon.

        Args:
            id (int): El número de la Pokédex.
            name (str): El nombre del Pokémon.
            type1 (str): El tipo primario del Pokémon.
            type2 (Optional[str]): El tipo secundario del Pokémon (puede ser None).
            hp (int): Puntos de salud base.
            attack (int): Estadística de ataque físico base.
            defense (int): Estadística de defensa física base.
            sp_atk (int): Estadística de ataque especial base.
            sp_def (int): Estadística de defensa especial base.
            speed (int): Estadística de velocidad base.
            imagen (str): La ruta al archivo de imagen del Pokémon.
        """
        self.id = id
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_atk = sp_atk
        self.sp_def = sp_def
        self.speed = speed
        self.imagen = imagen
        self.movimientos: List[Movimiento] = [] # La lista de 4 movimientos se asignará después

    def asignar_movimientos(self, movimientos: List[Movimiento]):
        """Asigna una lista de hasta 4 movimientos al Pokémon."""
        if len(movimientos) <= 4:
            self.movimientos = movimientos
        else:
            # Opcional: lanzar un error si se intentan asignar más de 4 movimientos
            raise ValueError("Un Pokémon no puede tener más de 4 movimientos.")

    def __repr__(self):
        """Devuelve una representación en string del objeto."""
        return f"Pokemon(id={self.id}, name='{self.name}', type1='{self.type1}')"


class Entrenador:
    """
    Representa a un entrenador Pokémon con su equipo.
    """
    def __init__(self, id: int, name: str, imagen: str):
        """
        Inicializa una nueva instancia de Entrenador.

        Args:
            id (int): El identificador único para el entrenador.
            name (str): El nombre del entrenador.
            imagen (str): La ruta al archivo de imagen del entrenador.
        """
        self.id = id
        self.name = name
        self.imagen = imagen
        self.pokemons: List[Pokemon] = [] # El equipo de 3 Pokémon se asignará después

    def asignar_equipo(self, equipo: List[Pokemon]):
        """Asigna una lista de hasta 3 Pokémon al equipo del entrenador."""
        if len(equipo) <= 3:
            self.pokemons = equipo
        else:
            raise ValueError("Un entrenador no puede tener más de 3 Pokémon en su equipo.")
            
    def __repr__(self):
        """Devuelve una representación en string del objeto."""
        nombres_pokemon = [p.name for p in self.pokemons]
        return f"Entrenador(id={self.id}, name='{self.name}', equipo={nombres_pokemon})"
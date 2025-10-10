import time
from PIL import Image

# --- Importaciones de tus otros archivos ---
from data import crear_todos_los_entrenadores
from classes import Pokemon, Entrenador, Movimiento
from danio import calcular_danio, ko
from reward import calcular_reward_turno
from image_generator import crear_imagen_combate # <<< NUEVA IMPORTACIÓN

class Combate:
    def __init__(self, entrenador1: Entrenador, entrenador2: Entrenador):
        self.t1 = entrenador1
        self.t2 = entrenador2
        self.vidas_equipo_t1 = {p.name: p.hp for p in self.t1.pokemons}
        self.vidas_equipo_t2 = {p.name: p.hp for p in self.t2.pokemons}
        self.pokemon_activo_t1 = self.t1.pokemons[0]
        self.pokemon_activo_t2 = self.t2.pokemons[0]
        self.vida_actual_t1 = self.vidas_equipo_t1[self.pokemon_activo_t1.name]
        self.vida_actual_t2 = self.vidas_equipo_t2[self.pokemon_activo_t2.name]
        self.pokemon_left_t1 = len(self.t1.pokemons)
        self.pokemon_left_t2 = len(self.t2.pokemons)
        self.turno = 0
        self.log_del_turno = [] # <<< NUEVO: para guardar mensajes

    def _agregar_al_log(self, mensaje):
        """Añade un mensaje al log del turno."""
        self.log_del_turno.append(mensaje)

    def mostrar_estado_turno(self):
        salud_t1_porc = (self.vida_actual_t1 / self.pokemon_activo_t1.hp) * 100 if self.pokemon_activo_t1.hp > 0 else 0
        salud_t2_porc = (self.vida_actual_t2 / self.pokemon_activo_t2.hp) * 100 if self.pokemon_activo_t2.hp > 0 else 0
        self._agregar_al_log(f"{self.t1.name}: {self.pokemon_activo_t1.name} {self.vida_actual_t1:.0f}/{self.pokemon_activo_t1.hp} HP ({salud_t1_porc:.1f}%)")
        self._agregar_al_log(f"{self.t2.name}: {self.pokemon_activo_t2.name} {self.vida_actual_t2:.0f}/{self.pokemon_activo_t2.hp} HP ({salud_t2_porc:.1f}%)")

    def elegir_accion_jugador(self):
        # ... (sin cambios)
        print(f"\nElige una acción para {self.pokemon_activo_t1.name}:")
        for i, mov in enumerate(self.pokemon_activo_t1.movimientos):
            print(f"  {i+1}: {mov.name} (Tipo: {mov.type})")
        print(f"  5: Cambiar Pokémon")
        while True:
            try:
                eleccion = int(input("Introduce el número de la acción (1-5): "))
                if 1 <= eleccion <= 4: return self.pokemon_activo_t1.movimientos[eleccion - 1]
                elif eleccion == 5: return "CAMBIAR"
                else: print("Número no válido.")
            except (ValueError, IndexError): print("Entrada no válida.")

    def _elegir_siguiente_pokemon_jugador(self, forzado: bool = False):
        # ... (sin cambios)
        self.vidas_equipo_t1[self.pokemon_activo_t1.name] = self.vida_actual_t1
        while True:
            print("\nElige un Pokémon para cambiar:")
            pokemon_vivos = [p for p in self.t1.pokemons if self.vidas_equipo_t1[p.name] > 0]
            for i, poke in enumerate(pokemon_vivos):
                print(f"  {i+1}: {poke.name} ({self.vidas_equipo_t1[poke.name]}/{poke.hp} HP)")
            try:
                eleccion = int(input("Introduce el número del Pokémon: "))
                nuevo_pokemon = pokemon_vivos[eleccion - 1]
                if nuevo_pokemon.name == self.pokemon_activo_t1.name and not forzado:
                    print(f"{nuevo_pokemon.name} ya está en combate.")
                    continue
                self.pokemon_activo_t1 = nuevo_pokemon
                self.vida_actual_t1 = self.vidas_equipo_t1[nuevo_pokemon.name]
                self._agregar_al_log(f"\n¡{self.t1.name} saca a {self.pokemon_activo_t1.name}!")
                return True
            except (ValueError, IndexError): print("Selección no válida.")

    def elegir_movimiento_bot(self):
        return self.pokemon_activo_t2.movimientos[0]
    
    def ejecutar_ataque(self, atacante, defensor, mov):
        self._agregar_al_log(f"\n{atacante.name} utiliza {mov.name}...")
        # <<< CAMBIO: danio.py ya no debe imprimir. Asumimos que devuelve (daño, [mensajes])
        # Si danio.py sigue imprimiendo, esos mensajes no aparecerán en la imagen.
        danio_calculado = calcular_danio(atacante, defensor, mov)
        
        if danio_calculado > 0:
            porcentaje_danio = (danio_calculado / defensor.hp) * 100 if defensor.hp > 0 else 0
            self._agregar_al_log(f"...hizo {porcentaje_danio:.2f}% de daño.")
        return danio_calculado

    def manejar_debilitado(self, num_entrenador_debilitado):
        if num_entrenador_debilitado == 1:
            self._agregar_al_log(f"\n¡{self.pokemon_activo_t1.name} ha sido debilitado!")
            self.vidas_equipo_t1[self.pokemon_activo_t1.name] = 0
            self.pokemon_left_t1 -= 1
            if self.pokemon_left_t1 > 0: self._elegir_siguiente_pokemon_jugador(forzado=True)
        else:
            self._agregar_al_log(f"\n¡{self.pokemon_activo_t2.name} ha sido debilitado!")
            self.vidas_equipo_t2[self.pokemon_activo_t2.name] = 0
            self.pokemon_left_t2 -= 1
            if self.pokemon_left_t2 > 0:
                siguiente_pokemon_bot = next(p for p in self.t2.pokemons if self.vidas_equipo_t2[p.name] > 0)
                self.pokemon_activo_t2 = siguiente_pokemon_bot
                self.vida_actual_t2 = self.vidas_equipo_t2[siguiente_pokemon_bot.name]
                self._agregar_al_log(f"{self.t2.name} saca a {siguiente_pokemon_bot.name}!")

    def _agregar_estado_final_al_log(self):
        """Añade el estado de salud final al log del turno."""
        self._agregar_al_log("\n--- Estado Final del Turno ---")
        self._agregar_al_log(f"-> {self.pokemon_activo_t1.name}: {self.vida_actual_t1:.0f}/{self.pokemon_activo_t1.hp} HP")
        self._agregar_al_log(f"-> {self.pokemon_activo_t2.name}: {self.vida_actual_t2:.0f}/{self.pokemon_activo_t2.hp} HP")

    def simular(self):
        log_turno_anterior = "¡COMIENZA EL COMBATE!"
        
        while self.pokemon_left_t1 > 0 and self.pokemon_left_t2 > 0:
            self.turno += 1
            self.log_del_turno = [] # Limpiamos el log para el nuevo turno

            # <<< GENERACIÓN Y VISUALIZACIÓN DE LA IMAGEN >>>
            crear_imagen_combate(
                self.t1, self.pokemon_activo_t1, self.vida_actual_t1,
                self.t2, self.pokemon_activo_t2, self.vida_actual_t2,
                log_turno_anterior,
                output_path="estado_actual.png"
            )
            print("\n>> La imagen del combate se ha actualizado en 'estado_actual.png' <<")

            # Imprimimos el log anterior en consola para consistencia
            print("\n" + "="*20)
            print(log_turno_anterior)
            print("="*20 + "\n")

            self._agregar_al_log(f"==== TURNO {self.turno} ====")
            self.mostrar_estado_turno()
            
            # --- Lógica del turno ---
            accion_jugador = self.elegir_accion_jugador()
            
            if accion_jugador == "CAMBIAR":
                self._elegir_siguiente_pokemon_jugador()
                mov_bot = self.elegir_movimiento_bot()
                danio_recibido = self.ejecutar_ataque(self.pokemon_activo_t2, self.pokemon_activo_t1, mov_bot)
                self.vida_actual_t1 = max(0, self.vida_actual_t1 - danio_recibido)
                if self.vida_actual_t1 <= 0: self.manejar_debilitado(1)
                
            else: # Lógica de ataque
                mov_jugador = accion_jugador
                mov_bot = self.elegir_movimiento_bot()
                danio_turno_jugador, danio_turno_bot = 0, 0
                
                ataques = [{'atacante': self.pokemon_activo_t1, 'defensor': self.pokemon_activo_t2, 'mov': mov_jugador},
                           {'atacante': self.pokemon_activo_t2, 'defensor': self.pokemon_activo_t1, 'mov': mov_bot}]
                if self.pokemon_activo_t1.speed < self.pokemon_activo_t2.speed:
                    ataques.reverse()

                for ataque in ataques:
                    danio = self.ejecutar_ataque(ataque['atacante'], ataque['defensor'], ataque['mov'])
                    if ataque['atacante'] == self.pokemon_activo_t1:
                        self.vida_actual_t2 = max(0, self.vida_actual_t2 - danio)
                        danio_turno_jugador = danio
                        if self.vida_actual_t2 <= 0: self.manejar_debilitado(2); break
                    else:
                        self.vida_actual_t1 = max(0, self.vida_actual_t1 - danio)
                        danio_turno_bot = danio
                        if self.vida_actual_t1 <= 0: self.manejar_debilitado(1); break
                
                if self.vida_actual_t1 > 0 and self.vida_actual_t2 > 0:
                    reward = calcular_reward_turno(danio_turno_jugador, danio_turno_bot, self.pokemon_activo_t1, self.pokemon_activo_t2, mov_jugador, mov_bot)
                    self._agregar_al_log(f"\nreward turno {self.turno}: {reward:.2f}")

            self._agregar_estado_final_al_log()
            # Preparamos el log para el siguiente turno
            log_turno_anterior = "\n".join(self.log_del_turno)

        # Fin del combate
        print("\n\n====== ¡FIN DEL COMBATE! ======")
        if self.pokemon_left_t1 > 0: print(f"¡El ganador es {self.t1.name}!")
        else: print(f"¡El ganador es {self.t2.name}!")

if __name__ == "__main__":
    print("Cargando datos para el combate...")
    todos_los_entrenadores = crear_todos_los_entrenadores()
    
    if len(todos_los_entrenadores) >= 2:
        jugador1 = todos_los_entrenadores[0]
        bot = todos_los_entrenadores[1]
        combate_actual = Combate(jugador1, bot)
        combate_actual.simular()
    else:
        print("Error: Se necesitan al menos 2 entrenadores en 'trainer_pokemon.csv'.")
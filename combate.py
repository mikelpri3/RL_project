import time
from PIL import Image

# --- Importaciones de tus otros archivos ---
from data import crear_todos_los_entrenadores
from classes import Pokemon, Entrenador, Movimiento
from danio import calcular_danio, ko
from reward import calcular_reward_turno
from image_generator import crear_imagen_combate # <<< NUEVA IMPORTACIÓN
from types import SimpleNamespace

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

    # --- RL ADAPTER: estado + acciones + un paso (turno) ---

    def estado_raw(self):
        """
        Estado raw suficiente para construir una observación discreta (episodios).
        Observation the agent can learn from.
        """
        a = self.pokemon_activo_t1
        b = self.pokemon_activo_t2
        return {
            # HP totales (base del pokémon) y vida actual del combate
            "our_hp_total": a.hp,
            "our_hp_actual": self.vida_actual_t1,
            "opp_hp_total": b.hp,
            "opp_hp_actual": self.vida_actual_t2,
            # Tipos (pueden ser None)
            "our_type1": a.type1, "our_type2": a.type2,
            "opp_type1": b.type1, "opp_type2": b.type2,
            # Equipo restante
            "our_team_left": self.pokemon_left_t1,
            "opp_team_left": self.pokemon_left_t2,
            # Slots disponibles para cambiar (índices del equipo t1 con vida>0 y no el activo)
            "switch_slots_alive": [i for i,p in enumerate(self.t1.pokemons)
                                if self.vidas_equipo_t1[p.name] > 0 and p.name != a.name],
            # Cuántos movimientos tiene el activo del agente ahora mismo
            "n_moves": len(a.movimientos)
        }

    def acciones_legales_agente(self):
        """
        Devuelve una lista de acciones legales:
        - 0..3: usar movimiento i (si existe)
        - 10+idx_equipo: cambiar al pokémon del equipo con ese índice (si está vivo y no es el activo)
        """
        a = self.pokemon_activo_t1
        acc = [i for i in range(len(a.movimientos))]  # 0..n_moves-1
        # switches
        for i, p in enumerate(self.t1.pokemons):
            if self.vidas_equipo_t1[p.name] > 0 and p.name != a.name:
                acc.append(10 + i)  # 10+slot = acción de cambio
        return acc

    def _aplicar_cambio_agente(self, idx_equipo):
        """Cambia el pokémon activo del agente al slot idx_equipo (si está vivo)."""
        nuevo = self.t1.pokemons[idx_equipo]
        if self.vidas_equipo_t1[nuevo.name] <= 0:
            return False
        self.pokemon_activo_t1 = nuevo
        self.vida_actual_t1 = self.vidas_equipo_t1[nuevo.name]
        self._agregar_al_log(f"\n¡{self.t1.name} saca a {self.pokemon_activo_t1.name}!")
        return True

    def step_rl(self, agent_action):
        """
        Ejecuta UN turno de combate desde el estado actual:
        - Si agent_action in [0..3]: usar ese movimiento (si existe).
        - Si agent_action = 10+idx: cambiar al pokémon del slot idx (si está vivo).
        Devuelve: (reward_turno, done_bool)
        """
        self.turno += 1
        self.log_del_turno = []  # limpiamos el log de este turno

        # Guardamos info del inicio del turno (para la reward)
        oponente_al_inicio = self.pokemon_activo_t2
        vida_oponente_antes_ataques = self.vida_actual_t2
        vida_jugador_antes_ataques  = self.vida_actual_t1

        danio_turno_jugador = 0.0
        danio_turno_bot     = 0.0

        # ---- Acción del agente: mover o cambiar ----
        if isinstance(agent_action, int) and agent_action >= 10:
            # Cambio de pokémon
            idx = agent_action - 10
            ok = self._aplicar_cambio_agente(idx)
            mov_jugador = None  # no hay movimiento si hay cambio
        else:
            # Usar movimiento i
            a = self.pokemon_activo_t1
            if agent_action < 0 or agent_action >= len(a.movimientos):
                # acción inválida -> no hace nada (penalización será implícita vía reward baja)
                mov_jugador = None
            else:
                mov_jugador = a.movimientos[agent_action]

        # --- Movimiento del bot (misma política que antes) ---
        mov_bot = self.elegir_movimiento_bot()

        # --- Orden de turnos por Speed (igual que simular) ---
        ataques = []
        if mov_jugador is not None:
            ataques.append({'atacante': self.pokemon_activo_t1, 'defensor': self.pokemon_activo_t2, 'mov': mov_jugador})
        # Si hubo cambio, el agente no ataca este turno → su ataque no se encola
        ataques.append({'atacante': self.pokemon_activo_t2, 'defensor': self.pokemon_activo_t1, 'mov': mov_bot})

        # Si ambos atacan, decide por speed (si empatan, va primero el agente, como en README)
        if len(ataques) == 2:
            if self.pokemon_activo_t1.speed < self.pokemon_activo_t2.speed:
                ataques.reverse()

        vida_oponente_ko_param, vida_jugador_ko_param = None, None

        # --- Resolver ataques en orden (reutiliza ejecutar_ataque y manejar_debilitado) ---
        for ataque in ataques:
            danio = 0.0
            if ataque['mov'] is not None:  # puede ser None si el agente cambió
                danio = self.ejecutar_ataque(ataque['atacante'], ataque['defensor'], ataque['mov'])

            if ataque['atacante'] == self.pokemon_activo_t1:
                self.vida_actual_t2 = max(0, self.vida_actual_t2 - danio)
                danio_turno_jugador = danio
                if self.vida_actual_t2 <= 0:
                    vida_oponente_ko_param = vida_oponente_antes_ataques
                    self.manejar_debilitado(2)
                    break  # si K.O., termina el turno
            else:
                self.vida_actual_t1 = max(0, self.vida_actual_t1 - danio)
                danio_turno_bot = danio
                if self.vida_actual_t1 <= 0:
                    vida_jugador_ko_param = vida_jugador_antes_ataques
                    self.manejar_debilitado(1)
                    break
    
        mov_j_for_reward = mov_jugador if mov_jugador is not None else SimpleNamespace(name="Cambio")
        mov_b_for_reward = mov_bot      if mov_bot      is not None else SimpleNamespace(name="(bot_none)")
        # --- Reward del turno (usando tu reward.py como en simular) ---
        reward = calcular_reward_turno(
            danio_turno_jugador, danio_turno_bot,
            self.pokemon_activo_t1, self.pokemon_activo_t2,
            mov_j_for_reward, mov_b_for_reward,
            oponente_al_inicio,
            vida_oponente_antes_ko=vida_oponente_ko_param,
            vida_jugador_antes_ko=vida_jugador_ko_param
        )

        # --- ¿Fin del combate? El mismo criterio del final de simular ---
        done = (self.pokemon_left_t1 == 0) or (self.pokemon_left_t2 == 0)

        return reward, done


    def simular(self):
        log_turno_anterior = "¡COMIENZA EL COMBATE!"
        
        while self.pokemon_left_t1 > 0 and self.pokemon_left_t2 > 0:
            self.turno += 1
            self.log_del_turno = []

            crear_imagen_combate(
                entrenador1=self.t1, entrenador2=self.t2,
                texto_combate=log_turno_anterior,
                pokemon_left1=self.pokemon_left_t1, # <<< AÑADIR
                pokemon_left2=self.pokemon_left_t2, # <<< AÑADIR
                pokemon1=self.pokemon_activo_t1, vida_actual1=self.vida_actual_t1,
                pokemon2=self.pokemon_activo_t2, vida_actual2=self.vida_actual_t2,
                output_path="estado_actual.png"
            )
            print("\n>> La imagen del combate se ha actualizado en 'estado_actual.png' <<")
            print("\n" + "="*20, f"\n{log_turno_anterior}\n", "="*20 + "\n")

            self._agregar_al_log(f"==== TURNO {self.turno} ====")
            self.mostrar_estado_turno()
            
            # ... (Toda la lógica del turno dentro del bucle while permanece exactamente igual) ...
            accion_jugador = self.elegir_accion_jugador()
            if accion_jugador == "CAMBIAR":
                self._elegir_siguiente_pokemon_jugador()
                mov_bot = self.elegir_movimiento_bot()
                danio_recibido = self.ejecutar_ataque(self.pokemon_activo_t2, self.pokemon_activo_t1, mov_bot)
                self.vida_actual_t1 = max(0, self.vida_actual_t1 - danio_recibido)
                if self.vida_actual_t1 > 0:
                    mov_cambio = Movimiento(id=0, name="Cambio", type="Normal", special=False, damage=0, precision=100)
                    reward = calcular_reward_turno(0, danio_recibido, self.pokemon_activo_t1, self.pokemon_activo_t2, mov_cambio, mov_bot)
                    self._agregar_al_log(f"\nreward turno {self.turno}: {reward:.2f}")
                if self.vida_actual_t1 <= 0: self.manejar_debilitado(1)
            else:
                mov_jugador = accion_jugador
                mov_bot = self.elegir_movimiento_bot()
                danio_turno_jugador, danio_turno_bot = 0, 0
                oponente_al_inicio_del_turno = self.pokemon_activo_t2
                vida_jugador_antes_ataques = self.vida_actual_t1
                vida_oponente_antes_ataques = self.vida_actual_t2
                ataques = [{'atacante': self.pokemon_activo_t1, 'defensor': self.pokemon_activo_t2, 'mov': mov_jugador},
                           {'atacante': self.pokemon_activo_t2, 'defensor': self.pokemon_activo_t1, 'mov': mov_bot}]
                if self.pokemon_activo_t1.speed < self.pokemon_activo_t2.speed: ataques.reverse()
                vida_oponente_ko_param, vida_jugador_ko_param = None, None
                for ataque in ataques:
                    danio = self.ejecutar_ataque(ataque['atacante'], ataque['defensor'], ataque['mov'])
                    if ataque['atacante'] == self.pokemon_activo_t1:
                        self.vida_actual_t2 = max(0, self.vida_actual_t2 - danio)
                        danio_turno_jugador = danio
                        if self.vida_actual_t2 <= 0:
                            vida_oponente_ko_param = vida_oponente_antes_ataques
                            self.manejar_debilitado(2); break
                    else:
                        self.vida_actual_t1 = max(0, self.vida_actual_t1 - danio)
                        danio_turno_bot = danio
                        if self.vida_actual_t1 <= 0:
                            vida_jugador_ko_param = vida_jugador_antes_ataques
                            self.manejar_debilitado(1); break
                reward = calcular_reward_turno(danio_turno_jugador, danio_turno_bot, self.pokemon_activo_t1, self.pokemon_activo_t2, mov_jugador, mov_bot, oponente_al_inicio_del_turno, vida_oponente_antes_ko=vida_oponente_ko_param, vida_jugador_antes_ko=vida_jugador_ko_param)
                log_msg = f"\nreward turno {self.turno}"
                if vida_oponente_ko_param is not None or vida_jugador_ko_param is not None: log_msg += " (KO)"
                log_msg += f": {reward:.2f}"
                self._agregar_al_log(log_msg)
            
            self._agregar_estado_final_al_log()
            log_turno_anterior = "\n".join(self.log_del_turno)

        # <<< NUEVA LÓGICA DE FIN DE COMBATE >>>
        self.log_del_turno = [] # Limpiamos el log para el mensaje final
        self._agregar_al_log("====== ¡FIN DEL COMBATE! ======")
        
        ganador_es_jugador1 = self.pokemon_left_t1 > 0
        
        if ganador_es_jugador1:
            self._agregar_al_log(f"\n¡El ganador es {self.t1.name}!")
            # La recompensa final por ganar puede ser un valor alto, como +10
            recompensa_final = 10.0
        else:
            self._agregar_al_log(f"\n¡El ganador es {self.t2.name}!")
            # La recompensa final por perder puede ser un valor negativo, como -10
            recompensa_final = -10.0
            
        self._agregar_al_log(f"\nRecompensa Final: {recompensa_final:.2f}")
        
        log_final = "\n".join(self.log_del_turno)

        # Generamos la imagen final, pasando None para el Pokémon del perdedor
        crear_imagen_combate(
            entrenador1=self.t1, entrenador2=self.t2,
            texto_combate=log_final,
            pokemon_left1=self.pokemon_left_t1, # <<< AÑADIR
            pokemon_left2=self.pokemon_left_t2, # <<< AÑADIR
            pokemon1=self.pokemon_activo_t1 if ganador_es_jugador1 else None,
            vida_actual1=self.vida_actual_t1 if ganador_es_jugador1 else 0,
            pokemon2=self.pokemon_activo_t2 if not ganador_es_jugador1 else None,
            vida_actual2=self.vida_actual_t2 if not ganador_es_jugador1 else 0,
            output_path="estado_actual.png"
        )

        # Fin del combate (sin cambios)
        print("\n\n====== ¡FIN DEL COMBATE! ======")
        if self.pokemon_left_t1 > 0: print(f"¡El ganador es {self.t1.name}!")
        else: print(f"¡El ganador es {self.t2.name}!")

if __name__ == "__main__":
    print("Cargando datos para el combate...")
    todos_los_entrenadores = crear_todos_los_entrenadores()
    
    if len(todos_los_entrenadores) >= 2:
        jugador1 = todos_los_entrenadores[1]
        bot = todos_los_entrenadores[2]
        combate_actual = Combate(jugador1, bot)
        combate_actual.simular()
    else:
        print("Error: Se necesitan al menos 2 entrenadores en 'trainer_pokemon.csv'.")
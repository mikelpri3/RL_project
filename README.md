# RL_project
Proyecto Reinforcement Learning

---

# Explicación Enviroment:
    - Un agente que aprende mediante RL en contra de un bot el cual siempre realiza las mismas acciones

    - Enviroment propio para combates pokemon, con movimientos, calculos de daño e interfaz propia. Aunque la mayoría está basado en los juegos originales.
    - Las estadísticas de los pokemon, los tipos y el sistema de combate se basan al 100% en los juegos originales
    - Los pokemon no tienen habilidades, objetos, naturalezas, IV o EVs. Con tal de simplificar el enviroment

    - Combate individual entre 2 entrenadores (el agente y el bot)
    - Cada entrenador tiene 3 pokemon
    - Cada pokemon tiene 4 movimientos
    - El agente puede variar entre movimientos y cambiar de pokemon
    - El bot solo hace el primer movimiento en la lista de movs de ese pokemon
    - El bot no puede cambiar de pokemon
    - Si un pokemon del agente muere, el agente puede elegir que otro pokemon sacar
    - Si un pokemon del bot muere, el bot manda el siguiente en su lista ordenada de pokemon

    - El primer entrenador que mate a los 3 pokemons del rival gana

---

# Cálculo Daño movimiento:
Tenemos nuestra propia fórmula para el calculo de daño en nuestro enviroment

El daño que inflinge un movimiento, determina cuantos HP/PS pierde el pokemon rival

La cual está basada en la fórmula original de los juegos de pokémon

**Si el movimiento es especial:**

    danio = mov.damage * efectividad_total * multiplicador_stab * (pokemon_atacante.sp_atk / pokemon_defensor.sp_def) * 0.2

**Si el movimiento es físico:**

    danio = mov.damage * efectividad_total * multiplicador_stab * (pokemon_atacante.attack / pokemon_defensor.defense) * 0.2

**Movimientos**

Los movimientos tienen un tipo, un damage, un accuracy y pueden ser físicos/especiales

Hay un número random de 1-100, si el accuracy es menor al número random: danio=0  independientemente del resto de parámetros

Por ejemplo: 

    - Ejemplo físico: Hidroariete es tipo Agua, tiene 100 de damage, 90 de accuracy

    - Ejemplo especial: Lanzallamas es tipo Fuego, tiene 90 de damaga, 100 de accuracy

**Efectividad**

La efectividad es que tan efectivo es el movimiento utilizado comparando con el tipo del pokemon defensor

Se calcula mediante la tabla de tipos, la cual calcula la efectividad ofensiva/defensiva entre dos tipos

Este valor puede ser 0, 0.5, 1, 2

Ya que los pokemons pueden tener un máximo de 2 tipos, la efectividad_total puede ser 0, 0.25, 0.5, 1, 2, 4

Por ejemplo:

    - Ataque fuego vs Pokemon Agua --> efectividad_total = 0.5

    - Ataque agua vs Pokemon Fuego --> efectividad_total = 2

    - Ataque planta vs Pokemon normal --> efectividad_total = 1

    - Ataque fuego vs Pokemon Planta Agua --> efectividad_total = 1

    - Ataque fuego vs Pokemon Agua Roca --> efectividad_total = 0.25

    - Ataque fuego vs Pokemon Planta Hielo --> efectividad = 4

    - Ataque normal vs Pokemon Fantasma --> efectividad = 0


**STAB**

STAB o Same Type Attack Bonus es un multiplicador que se activa si el movimiento utilizado coincide con alguno de los tipos del pokemon que lo lanza, dando un 50% de daño extra

Por ejemplo:

    - Si un charizard utiliza lanzallamas ---> STAB = 1.5

    - Si un pikachu utiliza lanzallamas ---> STAB = 1


**Estadísticas Pokemon**

Los pokemons pueden tener 1 o 2 tipos, tienen 4 movimientos y 6 estadísticas

HP,Attack,Defense,Sp.Atk,Sp.Def,Speed

    - HP (Health Points) o PS (Puntos de Salud): determinan cuanta vida tiene el pokemon, cuanta mayor vida, más golpes podrá resistir

    - Attack: determina cuanto daño hace los ataques físicos del pokémon, cuanto mayor el ataque, mayor será el daño que se haga

    - Defense: determina cuanto daño recibe de los ataques físicos de los pokémon rivales, cuanto mayor la defensa, resistirá mejor los ataques físicos

    - Sp.Atk: determina cuanto daño hace los ataques especiales del pokémon, cuanto mayor el ataque, mayor será el daño que se haga

    - Sp.Def: determina cuanto daño recibe de los ataques especiales de los pokémon rivales, cuanto mayor la defensa especial, resistirá mejor los ataques especiales

    - Speed: determina que pokemon se mueve primero en un turno, quien tenga la mayor speed atacará primero, en caso de empate, se moverá primero el agente

Por ejemplo: 

    - Pikachu es solo tipo Eléctrico, con HP: 35, Attack: 55, Defense: 40, Sp.Atk: 50, Sp.Def: 50, Speed: 90

    - Charizard es tipo Fuego Volador, con HP: 78, Attack: 84, Defense: 78, Sp.Atk: 109, Sp.Def: 85, Speed: 100

**Ejemplos Daño**

Charizard usa lanzallamas a Venusaur

danio = 90 * 2 * 1.5 * 109 / 100 * 0.2 = Venusaur pierde 58.86 PS

Pikachu usa lanzallamas a Blastoise

danio = 90 * 0.5 * 1 * 50 / 105 * 0.2 = Blastoise pierde 4.29 PS

---

# Reward Function

**Retos**

Uno de los mayores retos era que el agente pensase en escenarios futuros

Ya que si la reward function fuese simplemente la diferencia entre el daño hecho y el recibido, siempre vería los cambios de pokemon como algo negativo

Y por ejemplo, sacar un Charizard enfrente de un Venusaur debía verse como algo bueno, a pesar de que en ese turno el Charizard recibiese algo de daño

Otro de los retos es ver como premiar los K.O. , las efectividades entre pokemons y el ganar/perder el combate 

**Definición**

La reward function base sería esta:

> **reward = danio_hecho - danio_recibido + (efectividad_ofensiva / efectividad_defensiva) - 1**

Si se termina el combate:

    - si gana el agente: reward = +10
    - si gana el bot: reward = -10

danio_hecho (0-1) = % de salud quitado con el movimiento del agente al rival, 

    - si se falla el ataque o se cambia de pokemon, danio_hecho = 0
    - si hay K.O. danio_hecho es el % de los PS restantes que tenía el pokemon rival + 1

danio_recibido (0-1) = % de salud recibido del movimiento rival

    - si hay K.O. danio_recibido es el % de los PS restantes que tenía el pokemon del agente - 1

efectividad_ofensiva(0-4) = efectividad_total del movimiento utilizado contra el pokemon rival

    - si se cambia de pokemon, se revisa la lista de los 4 movimientos del pokemon cambiado, la efectividad_ofensiva será la efectividad_máxima que se encuentre

    - esto se hace ya que cuando cambias de pokemon no haces ningún movimiento, y así "prevees" si ofensivamente ha sido un buen cambio

efectividad_defensiva(0-4) = efectividad_total del movimiento recibido 

    - si efectividad_total = 0, para evitar dividir por 0, se pone un parche de efectividad_defensiva = 0.01

**Explicación**

El danio_hecho - danio_recibido es la base de la reward function, esto se hace para balancear por si un pokemon es muy ofensivo o muy defensivo

Se hace con % de daño, ya que hay pokemons con mucho HP y bajas defensas y viceversa

<br>

Se suma las efectividades_ofensivas / defensivas, ya que sino haces eso, cuando se cambia de pokemon el reward siempre sería negativo (ya que danio_hecho = 0)

Así premiamos mucho las decisiones desde el punto de vista de la tabla de tipos, la cual es la base principal de pokemon

Este valor se suma en vez de multiplicar los danios, ya que al hacer cambios el danio_hecho = 0, por tanto no tiene sentido multiplicarle la efectividad_ofensiva y el reward siempre sería negativo en caso de cambio

<br>

Por último el -1, lo cual no es un número al azar

Ya que en un escenario neutro, por ejemplo: 2 pokemon tipo fuego lanzandose llanzallamas el uno al otro

Ya que efectividad_ofensiva = efectividad_ofensiva  ----->  efectividad_ofensiva / efectividad_defensiva = 1

En un escenario neutro, las efectividades sumarían 1, por tanto se le resta 1 para que el reward sea simplemente la diferencia de daño

Lo cual terminará en un reward bajo entre -0.1 y 0.1

**Ajustes Reward Function**

La reward function se puede ajustar dependiendo de la situación

Se puede multiplicar / dividir ciertos parámetros para premiar más algunas cosas que otras

En vez de -1, se puede restar un número mayor, para que en las situaciones "neutras" el reward sea un poco negativo, así buscará si o sí jugar mejor que el bot

---

# ¿Cómo iniciar un combate manual?:
1. Hacer python combate_manual.py   en la terminal
2. mirar el estado_actual.png / Mirar el visualizador que te abra Windows
3. escribir en terminal el comando con la acción que quieras tomar

---

# EXTERNAL DATA:
# Pokemon Data
The data from the pokemon was taken from
https://gist.github.com/armgilles/194bcff35001e7eb53a2a8b441e8b2c6

---

# Link Pokemon images
The pokemon images were taken from
https://www.wikidex.net/

---

# Link Trainer images
The trainer images were taken from 
https://play.pokemonshowdown.com/sprites/trainers/



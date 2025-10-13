# image_generator.py

from PIL import Image, ImageDraw, ImageFont
from classes import Pokemon, Entrenador
import subprocess

# --- Constantes de configuración para la imagen ---
ANCHO_AREA_BATALLA = 1130
ANCHO_PANEL_TEXTO = 600
ANCHO_CANVAS = ANCHO_AREA_BATALLA + ANCHO_PANEL_TEXTO
ALTO_CANVAS = 720
COLOR_FONDO_BATALLA, COLOR_PANEL_TEXTO, COLOR_TEXTO_PANEL = (248, 248, 248), (40, 40, 40), (255, 255, 255)
TAMANIO_POKE_JUGADOR, TAMANIO_POKE_OPONENTE, TAMANIO_ENTRENADOR = (400, 400), (300, 300), (280, 280)

# <<< POSICIONES AJUSTADAS >>>
POS_ENTRENADOR_JUGADOR = (20, ALTO_CANVAS - TAMANIO_ENTRENADOR[1])
POS_POKE_JUGADOR = (260, ALTO_CANVAS - TAMANIO_POKE_JUGADOR[1] - 20) # Movido hacia arriba
POS_ENTRENADOR_OPONENTE = (ANCHO_AREA_BATALLA - TAMANIO_ENTRENADOR[0] - 20, 60) # Movido hacia abajo
POS_POKE_OPONENTE = (ANCHO_AREA_BATALLA - TAMANIO_POKE_OPONENTE[0] - 250, 100)

ANCHO_BARRA_VIDA, ALTO_BARRA_VIDA, COLOR_BORDE_BARRA = 250, 20, (50, 50, 50)
COLOR_VERDE, COLOR_AMARILLO, COLOR_ROJO = (34, 177, 76), (255, 201, 14), (237, 28, 36)

# <<< NUEVAS CONSTANTES PARA LAS POKÉ BALLS >>>
TAMANIO_POKEBALL = (40, 40)
ESPACIO_POKEBALL = 10
POS_POKEBALLS_JUGADOR = (POS_ENTRENADOR_JUGADOR[0]+70, POS_ENTRENADOR_JUGADOR[1] - TAMANIO_POKEBALL[1] - 5)
POS_POKEBALLS_OPONENTE = (POS_ENTRENADOR_OPONENTE[0]+70, POS_ENTRENADOR_OPONENTE[1] - TAMANIO_POKEBALL[1] - 5)

def _get_color_vida(porcentaje_vida):
    if porcentaje_vida > 0.5: return COLOR_VERDE
    elif porcentaje_vida > 0.2: return COLOR_AMARILLO
    else: return COLOR_ROJO

def _dibujar_pokeballs(lienzo, pokeballs_vivas: int, pos_inicial: tuple, sprite_viva, sprite_derrotada):
    """Función auxiliar para dibujar las 3 Poké Balls de estado."""
    for i in range(3):
        pos_x = pos_inicial[0] + i * (TAMANIO_POKEBALL[0] + ESPACIO_POKEBALL)
        pos_y = pos_inicial[1]
        
        if i < pokeballs_vivas:
            lienzo.paste(sprite_viva, (pos_x, pos_y), sprite_viva)
        else:
            lienzo.paste(sprite_derrotada, (pos_x, pos_y), sprite_derrotada)

def crear_imagen_combate(
    entrenador1: Entrenador, entrenador2: Entrenador, texto_combate: str,
    pokemon_left1: int, pokemon_left2: int, # <<< NUEVOS PARÁMETROS
    pokemon1: Pokemon = None, vida_actual1: float = 0,
    pokemon2: Pokemon = None, vida_actual2: float = 0,
    output_path="combate.png"
):
    lienzo = Image.new('RGBA', (ANCHO_CANVAS, ALTO_CANVAS), COLOR_FONDO_BATALLA)
    
    try:
        sprite_entrenador1 = Image.open(entrenador1.imagen).convert("RGBA").resize(TAMANIO_ENTRENADOR)
        sprite_entrenador2 = Image.open(entrenador2.imagen).convert("RGBA").resize(TAMANIO_ENTRENADOR)
        lienzo.paste(sprite_entrenador1, POS_ENTRENADOR_JUGADOR, sprite_entrenador1)
        lienzo.paste(sprite_entrenador2, POS_ENTRENADOR_OPONENTE, sprite_entrenador2)

        if pokemon1:
            sprite_pokemon1 = Image.open(pokemon1.imagen).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT).resize(TAMANIO_POKE_JUGADOR)
            lienzo.paste(sprite_pokemon1, POS_POKE_JUGADOR, sprite_pokemon1)
        if pokemon2:
            sprite_pokemon2 = Image.open(pokemon2.imagen).convert("RGBA").resize(TAMANIO_POKE_OPONENTE)
            lienzo.paste(sprite_pokemon2, POS_POKE_OPONENTE, sprite_pokemon2)

        # <<< LÓGICA PARA DIBUJAR POKÉ BALLS >>>
        pokeball_viva = Image.open("assets/images/other_images/pokeball.png").convert("RGBA").resize(TAMANIO_POKEBALL)
        pokeball_derrotada = Image.open("assets/images/other_images/pokeball_derrotado.png").convert("RGBA").resize(TAMANIO_POKEBALL)
        
        _dibujar_pokeballs(lienzo, pokemon_left1, POS_POKEBALLS_JUGADOR, pokeball_viva, pokeball_derrotada)
        _dibujar_pokeballs(lienzo, pokemon_left2, POS_POKEBALLS_OPONENTE, pokeball_viva, pokeball_derrotada)

    except FileNotFoundError as e:
        print(f"Error al cargar imagen: {e}. Verifica la ruta de las imágenes.")
        return

    draw = ImageDraw.Draw(lienzo)
    try:
        font_nombre = ImageFont.truetype("assets/ttf/arial.ttf", 32)
        font_vida = ImageFont.truetype("assets/ttf/arial.ttf", 22)
        font_panel = ImageFont.truetype("assets/ttf/consola.ttf", 26)
    except IOError:
        font_nombre = font_vida = font_panel = ImageFont.load_default()

    if pokemon1:
        caja_jugador_pos = (ANCHO_AREA_BATALLA - 400, ALTO_CANVAS - 180)
        draw.rectangle((caja_jugador_pos[0], caja_jugador_pos[1], caja_jugador_pos[0] + 350, caja_jugador_pos[1] + 120), fill=(240, 240, 240), outline=COLOR_BORDE_BARRA, width=4)
        draw.text((caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 10), pokemon1.name, font=font_nombre, fill=COLOR_BORDE_BARRA)
        porcentaje_vida_p1 = vida_actual1 / pokemon1.hp if pokemon1.hp > 0 else 0
        ancho_vida_actual_p1 = int(ANCHO_BARRA_VIDA * porcentaje_vida_p1)
        pos_barra_p1 = (caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 55)
        draw.text((caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 80), f"HP: {int(vida_actual1)}/{pokemon1.hp}", font=font_vida, fill=COLOR_BORDE_BARRA)
        draw.rectangle((pos_barra_p1[0], pos_barra_p1[1], pos_barra_p1[0] + ANCHO_BARRA_VIDA, pos_barra_p1[1] + ALTO_BARRA_VIDA), fill=(180, 180, 180), outline=COLOR_BORDE_BARRA)
        if ancho_vida_actual_p1 > 0:
            draw.rectangle((pos_barra_p1[0], pos_barra_p1[1], pos_barra_p1[0] + ancho_vida_actual_p1, pos_barra_p1[1] + ALTO_BARRA_VIDA), fill=_get_color_vida(porcentaje_vida_p1))

    if pokemon2:
        caja_oponente_pos = (50, 50)
        draw.rectangle((caja_oponente_pos[0], caja_oponente_pos[1], caja_oponente_pos[0] + 350, caja_oponente_pos[1] + 120), fill=(240, 240, 240), outline=COLOR_BORDE_BARRA, width=4)
        draw.text((caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 10), pokemon2.name, font=font_nombre, fill=COLOR_BORDE_BARRA)
        porcentaje_vida_p2 = vida_actual2 / pokemon2.hp if pokemon2.hp > 0 else 0
        draw.text((caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 80), f"HP: {int(vida_actual2)}/{pokemon2.hp}", font=font_vida, fill=COLOR_BORDE_BARRA)
        ancho_vida_actual_p2 = int(ANCHO_BARRA_VIDA * porcentaje_vida_p2)
        pos_barra_p2 = (caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 55)
        draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + ANCHO_BARRA_VIDA, pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=(180, 180, 180), outline=COLOR_BORDE_BARRA)
        if ancho_vida_actual_p2 > 0:
            draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + ancho_vida_actual_p2, pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=_get_color_vida(porcentaje_vida_p2))

    pos_panel = (ANCHO_AREA_BATALLA, 0)
    draw.rectangle((pos_panel[0], pos_panel[1], ANCHO_CANVAS, ALTO_CANVAS), fill=COLOR_PANEL_TEXTO)
    draw.multiline_text((pos_panel[0] + 25, 25), texto_combate, font=font_panel, fill=COLOR_TEXTO_PANEL)
    
    lienzo.save(output_path)

        # Llama al explorador de Windows para que abra la imagen.
    # WSL se encarga de traducir la ruta del archivo automáticamente.
    subprocess.run(["explorer.exe", output_path])
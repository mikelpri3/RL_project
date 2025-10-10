# image_generator.py

from PIL import Image, ImageDraw, ImageFont
from classes import Pokemon, Entrenador
from data import crear_todos_los_entrenadores # Para probar

# --- Constantes de configuración para la imagen ---
ANCHO_AREA_BATALLA = 1280
ANCHO_PANEL_TEXTO = 450
ANCHO_CANVAS = ANCHO_AREA_BATALLA + ANCHO_PANEL_TEXTO
ALTO_CANVAS = 720

# Colores
COLOR_FONDO_BATALLA = (248, 248, 248)
COLOR_PANEL_TEXTO = (40, 40, 40)
COLOR_TEXTO_PANEL = (255, 255, 255)

# Tamaños
TAMANIO_POKE_JUGADOR = (400, 400)
TAMANIO_POKE_OPONENTE = (300, 300)
TAMANIO_ENTRENADOR = (280, 280)

# Posiciones (x, y)
POS_ENTRENADOR_JUGADOR = (20, ALTO_CANVAS - TAMANIO_ENTRENADOR[1])
POS_POKE_JUGADOR = (260, ALTO_CANVAS - TAMANIO_POKE_JUGADOR[1] + 40)
POS_ENTRENADOR_OPONENTE = (ANCHO_AREA_BATALLA - TAMANIO_ENTRENADOR[0] - 20, 20)
POS_POKE_OPONENTE = (ANCHO_AREA_BATALLA - TAMANIO_POKE_OPONENTE[0] - 250, 100)

# Barras de vida
ANCHO_BARRA_VIDA = 250
ALTO_BARRA_VIDA = 20
COLOR_VERDE = (34, 177, 76)
COLOR_AMARILLO = (255, 201, 14)
COLOR_ROJO = (237, 28, 36)
COLOR_BORDE_BARRA = (50, 50, 50)


def _get_color_vida(porcentaje_vida):
    """Devuelve el color de la barra de vida según el porcentaje."""
    if porcentaje_vida > 0.5:
        return COLOR_VERDE
    elif porcentaje_vida > 0.2:
        return COLOR_AMARILLO
    else:
        return COLOR_ROJO

def crear_imagen_combate(
    entrenador1: Entrenador, pokemon1: Pokemon, vida_actual1: float,
    entrenador2: Entrenador, pokemon2: Pokemon, vida_actual2: float,
    texto_combate: str,
    output_path="combate.png"
):
    """
    Crea una imagen estática de una escena de combate con un panel de texto.
    """
    lienzo = Image.new('RGBA', (ANCHO_CANVAS, ALTO_CANVAS), COLOR_FONDO_BATALLA)
    
    try:
        sprite_entrenador1 = Image.open(entrenador1.imagen).convert("RGBA").resize(TAMANIO_ENTRENADOR)
        sprite_entrenador2 = Image.open(entrenador2.imagen).convert("RGBA").resize(TAMANIO_ENTRENADOR)
        sprite_pokemon1 = Image.open(pokemon1.imagen).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT).resize(TAMANIO_POKE_JUGADOR)
        sprite_pokemon2 = Image.open(pokemon2.imagen).convert("RGBA").resize(TAMANIO_POKE_OPONENTE)

        lienzo.paste(sprite_entrenador1, POS_ENTRENADOR_JUGADOR, sprite_entrenador1)
        lienzo.paste(sprite_entrenador2, POS_ENTRENADOR_OPONENTE, sprite_entrenador2)
        lienzo.paste(sprite_pokemon1, POS_POKE_JUGADOR, sprite_pokemon1)
        lienzo.paste(sprite_pokemon2, POS_POKE_OPONENTE, sprite_pokemon2)
    except FileNotFoundError as e:
        print(f"Error al cargar imagen: {e}")
        return

    draw = ImageDraw.Draw(lienzo)
    try:
        font_nombre = ImageFont.truetype("arial.ttf", 32)
        font_vida = ImageFont.truetype("arial.ttf", 22)
        font_panel = ImageFont.truetype("consola.ttf", 26)
    except IOError:
        font_nombre = font_vida = font_panel = ImageFont.load_default()

    # Caja del JUGADOR
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

    # Caja del OPONENTE
    caja_oponente_pos = (50, 50)
    draw.rectangle((caja_oponente_pos[0], caja_oponente_pos[1], caja_oponente_pos[0] + 350, caja_oponente_pos[1] + 120), fill=(240, 240, 240), outline=COLOR_BORDE_BARRA, width=4)
    draw.text((caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 10), pokemon2.name, font=font_nombre, fill=COLOR_BORDE_BARRA)
    
    # <<< CAMBIO: Se añade el texto del HP del rival >>>
    porcentaje_vida_p2 = vida_actual2 / pokemon2.hp if pokemon2.hp > 0 else 0
    draw.text((caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 80), f"HP: {int(vida_actual2)}/{pokemon2.hp}", font=font_vida, fill=COLOR_BORDE_BARRA)
    ancho_vida_actual_p2 = int(ANCHO_BARRA_VIDA * porcentaje_vida_p2)
    pos_barra_p2 = (caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 55)
    draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + ANCHO_BARRA_VIDA, pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=(180, 180, 180), outline=COLOR_BORDE_BARRA)
    if ancho_vida_actual_p2 > 0:
        draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + ancho_vida_actual_p2, pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=_get_color_vida(porcentaje_vida_p2))

    # Panel de texto
    pos_panel = (ANCHO_AREA_BATALLA, 0)
    draw.rectangle((pos_panel[0], pos_panel[1], ANCHO_CANVAS, ALTO_CANVAS), fill=COLOR_PANEL_TEXTO)
    draw.multiline_text((pos_panel[0] + 25, 25), texto_combate, font=font_panel, fill=COLOR_TEXTO_PANEL)
    
    lienzo.save(output_path)
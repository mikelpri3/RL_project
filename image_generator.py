# image_generator.py

from PIL import Image, ImageDraw, ImageFont
from classes import Pokemon, Entrenador
from data import crear_todos_los_entrenadores # Para probar

# --- Constantes de configuración para la imagen ---
# El ancho del canvas se divide en el área de batalla y el panel de texto
ANCHO_AREA_BATALLA = 1280
ANCHO_PANEL_TEXTO = 450
ANCHO_CANVAS = ANCHO_AREA_BATALLA + ANCHO_PANEL_TEXTO
ALTO_CANVAS = 720

# Colores
COLOR_FONDO = (248, 248, 248)
COLOR_PANEL_TEXTO = (40, 40, 40) # Gris oscuro
COLOR_TEXTO_PANEL = (255, 255, 255) # Blanco

# Tamaños de los sprites
TAMANIO_POKE_JUGADOR = (400, 400)
TAMANIO_POKE_OPONENTE = (300, 300)
TAMANIO_ENTRENADOR = (280, 280)

# Posiciones (x, y) - ajustadas para mayor separación
POS_ENTRENADOR_JUGADOR = (10, ALTO_CANVAS - TAMANIO_ENTRENADOR[1])
POS_POKE_JUGADOR = (250, ALTO_CANVAS - TAMANIO_POKE_JUGADOR[1] + 40) # Movido a la derecha
POS_POKE_OPONENTE = (ANCHO_AREA_BATALLA - TAMANIO_POKE_OPONENTE[0] - 150, 100)

# Configuración de las barras de vida (sin cambios)
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

def crear_imagen_combate(entrenador1: Entrenador, pokemon1: Pokemon,
                         entrenador2: Entrenador, pokemon2: Pokemon,
                         texto_combate: str,
                         output_path="combate.png"):
    """
    Crea una imagen estática de una escena de combate con un panel de texto.
    """
    # 1. Crear el lienzo de fondo
    lienzo = Image.new('RGBA', (ANCHO_CANVAS, ALTO_CANVAS), COLOR_FONDO)
    
    # 2. Cargar, redimensionar y pegar sprites (sin cambios de lógica)
    sprite_entrenador1 = Image.open(entrenador1.imagen).convert("RGBA").resize(TAMANIO_ENTRENADOR)
    sprite_pokemon1 = Image.open(pokemon1.imagen).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT).resize(TAMANIO_POKE_JUGADOR)
    sprite_pokemon2 = Image.open(pokemon2.imagen).convert("RGBA").resize(TAMANIO_POKE_OPONENTE)

    lienzo.paste(sprite_entrenador1, POS_ENTRENADOR_JUGADOR, sprite_entrenador1)
    lienzo.paste(sprite_pokemon1, POS_POKE_JUGADOR, sprite_pokemon1)
    lienzo.paste(sprite_pokemon2, POS_POKE_OPONENTE, sprite_pokemon2)

    # 3. Preparar para dibujar y cargar fuentes
    draw = ImageDraw.Draw(lienzo)
    try:
        font_nombre = ImageFont.truetype("arial.ttf", 32)
        font_vida = ImageFont.truetype("arial.ttf", 22)
        font_panel = ImageFont.truetype("consola.ttf", 24) # Fuente monoespaciada para el panel
    except IOError:
        print("Fuente 'arial.ttf' o 'consola.ttf' no encontrada. Usando fuentes por defecto.")
        font_nombre = font_vida = font_panel = ImageFont.load_default()

    # 4. Dibujar cajas de información (posiciones ajustadas)
    caja_jugador_pos = (ANCHO_AREA_BATALLA - 400, ALTO_CANVAS - 180)
    # ... (el código para dibujar la caja del jugador es idéntico, solo cambia la posición base)
    draw.rectangle(
        (caja_jugador_pos[0], caja_jugador_pos[1], caja_jugador_pos[0] + 350, caja_jugador_pos[1] + 120),
        fill=(240, 240, 240), outline=COLOR_BORDE_BARRA, width=4)
    draw.text((caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 10), pokemon1.name, font=font_nombre, fill=COLOR_BORDE_BARRA)
    draw.text((caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 80), f"HP: {pokemon1.hp}/{pokemon1.hp}", font=font_vida, fill=COLOR_BORDE_BARRA)
    pos_barra_p1 = (caja_jugador_pos[0] + 20, caja_jugador_pos[1] + 55)
    draw.rectangle((pos_barra_p1[0], pos_barra_p1[1], pos_barra_p1[0] + ANCHO_BARRA_VIDA, pos_barra_p1[1] + ALTO_BARRA_VIDA), fill=(180, 180, 180))
    draw.rectangle((pos_barra_p1[0], pos_barra_p1[1], pos_barra_p1[0] + int(ANCHO_BARRA_VIDA * (pokemon1.hp/pokemon1.hp)), pos_barra_p1[1] + ALTO_BARRA_VIDA), fill=_get_color_vida(1.0))

    caja_oponente_pos = (50, 50)
    # ... (el código para dibujar la caja del oponente es idéntico)
    draw.rectangle(
        (caja_oponente_pos[0], caja_oponente_pos[1], caja_oponente_pos[0] + 350, caja_oponente_pos[1] + 100),
        fill=(240, 240, 240), outline=COLOR_BORDE_BARRA, width=4)
    draw.text((caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 10), pokemon2.name, font=font_nombre, fill=COLOR_BORDE_BARRA)
    pos_barra_p2 = (caja_oponente_pos[0] + 20, caja_oponente_pos[1] + 55)
    vida_actual_p2 = pokemon2.hp * 0.4  # Simulado al 40%
    porcentaje_vida_p2 = vida_actual_p2 / pokemon2.hp
    draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + ANCHO_BARRA_VIDA, pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=(180, 180, 180))
    draw.rectangle((pos_barra_p2[0], pos_barra_p2[1], pos_barra_p2[0] + int(ANCHO_BARRA_VIDA * porcentaje_vida_p2), pos_barra_p2[1] + ALTO_BARRA_VIDA), fill=_get_color_vida(porcentaje_vida_p2))

    # 5. --- NUEVO: Dibujar el panel de texto y el texto del combate ---
    pos_panel = (ANCHO_AREA_BATALLA, 0)
    draw.rectangle(
        (pos_panel[0], pos_panel[1], pos_panel[0] + ANCHO_PANEL_TEXTO, ALTO_CANVAS),
        fill=COLOR_PANEL_TEXTO
    )
    # Usamos multiline_text para manejar los saltos de línea (\n) automáticamente
    draw.multiline_text(
        (pos_panel[0] + 20, 20), # Posición del texto con un padding
        texto_combate,
        font=font_panel,
        fill=COLOR_TEXTO_PANEL
    )
    
    # 6. Guardar la imagen final
    lienzo.save(output_path)
    print(f"¡Imagen de combate guardada en '{output_path}'!")


# --- BLOQUE PARA PROBAR LA FUNCIÓN DIRECTAMENTE ---
if __name__ == '__main__':
    entrenadores = crear_todos_los_entrenadores()

    if len(entrenadores) > 0:
        entrenador1 = entrenadores[0]
        
        # Buscamos específicamente a Blastoise y Venusaur
        blastoise = next((p for p in entrenador1.pokemons if p.name == "Blastoise"), None)
        venusaur = next((p for p in entrenador1.pokemons if p.name == "Venusaur"), None)

        if blastoise and venusaur:
            # Texto de ejemplo para el panel de combate
            texto_del_turno = (
                "------ TURNO 1 ------\n\n"
                "Blastoise utiliza Hidropulso,\n"
                "hace 20.62% de danio.\n"
                "Es poco efectivo...\n\n"
                "Venusaur utiliza Lluevehojas,\n"
                "hace 0% de danio.\n"
                "¡Blastoise ha esquivado el ataque!"
            )
            
            print("Creando imagen de combate con panel de texto...")
            crear_imagen_combate(entrenador1, blastoise, 
                                   entrenador1, venusaur,
                                   texto_del_turno)
        else:
            print("No se encontraron Blastoise o Venusaur en el equipo del trainer1.")
    else:
        print("No se encontraron entrenadores.")
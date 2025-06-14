import pygame
import sys
import math
import time
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- CONFIGURACIONES INICIALES ---
altura_boton = 40  # Ajustado para mejor visibilidad
medida_cuadro = 180  # Tamaño de la imagen tarjeta

# La parte trasera de cada tarjeta
nombre_imagen_oculta = "assets/oculta.png"
imagen_oculta = pygame.image.load(nombre_imagen_oculta)
imagen_oculta = pygame.transform.scale(imagen_oculta, (medida_cuadro, medida_cuadro))

segundos_mostrar_pieza = 2  # Tiempo a mostrar la pieza si es errónea

# Colores
color_blanco = (255, 255, 255)
color_negro = (0, 0, 0)
color_gris = (206, 206, 206)
color_azul = (30, 136, 229)

# Sonidos
sonido_fondo = pygame.mixer.Sound("assets/fondo.wav")
sonido_clic = pygame.mixer.Sound("assets/clic.wav")
sonido_exito = pygame.mixer.Sound("assets/ganador.wav")
sonido_fracaso = pygame.mixer.Sound("assets/equivocado.wav")
sonido_voltear = pygame.mixer.Sound("assets/voltear.wav")

# Fuente para textos y botones
tamanio_fuente = 24
fuente = pygame.font.SysFont("Arial", tamanio_fuente)

# --- CLASES Y FUNCIONES ---

class Cuadro:
    def __init__(self, fuente_imagen):
        self.mostrar = False
        self.descubierto = False
        self.fuente_imagen = fuente_imagen
        self.imagen_real = pygame.image.load(fuente_imagen)
        orig_width, orig_height = self.imagen_real.get_size()
        new_size = (int(orig_width * 0.8), int(orig_height * 0.8))
        self.imagen_real = pygame.transform.scale(self.imagen_real, new_size)


# Definir dificultades con número de pares y su distribución (columnas x filas)
dificultades = {
    "Fácil": {"pares": 4, "columnas": 4, "filas": 2},   # 4x2 = 8 cartas
    "Medio": {"pares": 6, "columnas": 4, "filas": 3},   # 4x3 = 12 cartas
    "Difícil": {"pares": 8, "columnas": 4, "filas": 4}  # 4x4 = 16 cartas
}

# Lista de imágenes disponibles
imagenes_disponibles = [
    "assets/TungTungTungSahur.png",
    "assets/Tralalero_tralala.png",
    "assets/capuccino.png",
    "assets/Chimpanzini_bananini.png",
    "assets/Tripi_tropi.png",
    "assets/Bombardiro_crocodilo.png",
    "assets/Br_br_patapim.png",
    "assets/Lirili_rili_ralila.png"
]

# Variables globales de juego
cuadros = []
anchura_pantalla = 0
altura_pantalla = 0
anchura_boton = 0
boton = None

# Estado del juego
ultimos_segundos = None
puede_jugar = True
juego_iniciado = False
juego_completado = False  # Nueva variable para indicar si el juego ha terminado

# Índices para tarjetas seleccionadas
x1 = None
y1 = None
x2 = None
y2 = None

# Función para generar cuadros en función de dificultad con filas y columnas fijos
def generar_cuadros(pares, columnas, filas):
    """Genera la matriz de cuadros con la cantidad exacta y distribución."""
    lista_cuadros = []
    seleccionadas = random.sample(imagenes_disponibles, pares)
    for img in seleccionadas:
        lista_cuadros.append(Cuadro(img))
        lista_cuadros.append(Cuadro(img))
    # Debemos asegurarnos que pares*2 == columnas*filas
    total_tarjetas = pares * 2
    if total_tarjetas != columnas * filas:
        raise ValueError(f"La cantidad total de tarjetas ({total_tarjetas}) no coincide con columnas ({columnas}) * filas ({filas})")
    random.shuffle(lista_cuadros)
    matriz = []
    for i in range(filas):
        fila = lista_cuadros[i*columnas:(i+1)*columnas]
        matriz.append(fila)
    return matriz

# Ocultar cuadros
def ocultar_todos_los_cuadros():
    for fila in cuadros:
        for cuadro in fila:
            cuadro.mostrar = False
            cuadro.descubierto = False

# Aleatorizar cuadros (mezclar posición)
def aleatorizar_cuadros():
    cantidad_filas = len(cuadros)
    cantidad_columnas = len(cuadros[0])
    for y in range(cantidad_filas):
        for x in range(cantidad_columnas):
            x_aleatorio = random.randint(0, cantidad_columnas - 1)
            y_aleatorio = random.randint(0, cantidad_filas - 1)
            cuadro_temporal = cuadros[y][x]
            cuadros[y][x] = cuadros[y_aleatorio][x_aleatorio]
            cuadros[y_aleatorio][x_aleatorio] = cuadro_temporal

def gana():
    for fila in cuadros:
        for cuadro in fila:
            if not cuadro.descubierto:
                return False
    return True

def comprobar_si_gana():
    global juego_completado  # Usar la variable de estado
    if gana():
        pygame.mixer.Sound.play(sonido_exito)
        juego_completado = True  # Marcar el juego como completado

def reiniciar_juego():
    global juego_iniciado, juego_completado
    juego_iniciado = False
    juego_completado = False  # Reiniciar el estado de completado

def iniciar_juego(config_dificultad):
    global pantalla_juego, juego_completado  # Asegurarse de actualizar juego_completado

    pygame.mixer.Sound.play(sonido_clic)
    global juego_iniciado, cuadros, anchura_pantalla, altura_pantalla, anchura_boton, boton
    global x1, y1, x2, y2, ultimos_segundos, puede_jugar

    pares = config_dificultad["pares"]
    columnas = config_dificultad["columnas"]
    filas = config_dificultad["filas"]

    cuadros = generar_cuadros(pares, columnas, filas)

    anchura_pantalla = columnas * medida_cuadro
    altura_pantalla = filas * medida_cuadro + altura_boton
    anchura_boton = anchura_pantalla
    boton = pygame.Rect(0, altura_pantalla - altura_boton, anchura_boton, altura_boton)

    # Redimensionar la ventana
    pantalla_juego = pygame.display.set_mode((anchura_pantalla, altura_pantalla))

    ocultar_todos_los_cuadros()
    juego_iniciado = True
    juego_completado = False  # RESETEAR ESTADO DE JUEGO COMPLETADO
    puede_jugar = True
    x1 = y1 = x2 = y2 = None
    ultimos_segundos = None
																			

# Menú inicial para seleccionar dificultad
def mostrar_menu():
    pantalla_juego = pygame.display.set_mode((600, 300))
    pygame.display.set_caption('Seleccionar Dificultad - Juego de Memoria')
    clock = pygame.time.Clock()
    opcion_seleccionada = None
    while opcion_seleccionada is None:
        pantalla_juego.fill(color_blanco)

        titulo = fuente.render("Selecciona Dificultad", True, color_negro)
        pantalla_juego.blit(titulo, (300 - titulo.get_width()//2, 30))

        for i, nombre in enumerate(dificultades.keys()):
            color = color_azul
            texto = fuente.render(nombre, True, color)
            rect_texto = texto.get_rect(center=(300, 100 + i*60))
            pantalla_juego.blit(texto, rect_texto)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, nombre in enumerate(dificultades.keys()):
                    rect_click = pygame.Rect(200, 80 + i*60, 200, 40)
                    if rect_click.collidepoint(x, y):
                        opcion_seleccionada = nombre

        pygame.display.update()
        clock.tick(60)
    return dificultades[opcion_seleccionada]

# --- PROGRAMA PRINCIPAL ---

# Escoger dificultad al iniciar
nivel_dificultad_config = mostrar_menu()

# Iniciar juego con dicha dificultad
iniciar_juego(nivel_dificultad_config)

pygame.display.set_caption('Juego de memoria en Python - Grupo1')
pygame.mixer.Sound.play(sonido_fondo, -1)
pantalla_juego = pygame.display.set_mode((anchura_pantalla, altura_pantalla))

# Variables para control de tarjetas descubiertas
x1 = None
y1 = None
x2 = None
y2 = None

ultimos_segundos = None
puede_jugar = True

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            xAbsoluto, yAbsoluto = event.pos
            
            # Solo permitir clic en tarjetas si se puede jugar
            if puede_jugar and not juego_completado and boton.collidepoint(event.pos) is False:
		   
				
					  
														
													  
				 
                if not juego_iniciado:
                    continue
                x = math.floor(xAbsoluto / medida_cuadro)
                y = math.floor(yAbsoluto / medida_cuadro)
                if y >= len(cuadros) or x >= len(cuadros[0]):
                    continue
                cuadro = cuadros[y][x]
                if cuadro.mostrar or cuadro.descubierto:
                    continue
                if x1 is None and y1 is None:
                    x1 = x
                    y1 = y
                    cuadros[y1][x1].mostrar = True
                    pygame.mixer.Sound.play(sonido_voltear)
                else:
                    x2 = x
                    y2 = y
                    cuadros[y2][x2].mostrar = True
                    cuadro1 = cuadros[y1][x1]
                    cuadro2 = cuadros[y2][x2]
                    if cuadro1.fuente_imagen == cuadro2.fuente_imagen:
                        cuadros[y1][x1].descubierto = True
                        cuadros[y2][x2].descubierto = True
                        x1 = y1 = x2 = y2 = None
                        pygame.mixer.Sound.play(sonido_clic)
                    else:
                        pygame.mixer.Sound.play(sonido_fracaso)
                        ultimos_segundos = int(time.time())
                        puede_jugar = False
                comprobar_si_gana()
            
            # Manejo del botón de menú (solo cuando el juego está completado)
            if boton.collidepoint(event.pos) and juego_completado:
                nivel_dificultad_config = mostrar_menu()
                iniciar_juego(nivel_dificultad_config)

    ahora = int(time.time())
    if ultimos_segundos is not None and ahora - ultimos_segundos >= segundos_mostrar_pieza:
        cuadros[y1][x1].mostrar = False
        cuadros[y2][x2].mostrar = False
        x1 = y1 = x2 = y2 = None
        ultimos_segundos = None
        puede_jugar = True

    pantalla_juego.fill(color_blanco)
    for y, fila in enumerate(cuadros):
        for x, cuadro in enumerate(fila):
            if cuadro.descubierto or cuadro.mostrar:
                pantalla_juego.blit(cuadro.imagen_real, (x * medida_cuadro, y * medida_cuadro))
            else:
                pantalla_juego.blit(imagen_oculta, (x * medida_cuadro, y * medida_cuadro))

    # Dibujar el botón solo cuando el juego está completado
    if juego_completado:
		 
        pygame.draw.rect(pantalla_juego, color_azul, boton)
        pantalla_juego.blit(fuente.render("Menú", True, color_blanco),
                            (anchura_boton//2 - 30, altura_pantalla - altura_boton + 8))
   
		   
				
					
					  

    pygame.display.update()
    clock.tick(60)

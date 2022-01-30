"""
--------------------------------------------------------------------------------
----------BATALLA ESPACIAL------------------------------------------------------
--------------------------------------------------------------------------------
----------SANTIAGO RIOS GUIRAL--------------------------------------------------
----------santiago.riosg@udea.edu.co--------------------------------------------
----------CC: 1152699366--------------------------------------------------------
--------------------------------------------------------------------------------
----------EMMANUEL GOMEZ OSPINA-------------------------------------------------
----------emmanuel.gomezo@udea.edu.co-------------------------------------------
----------CC: 1005872591--------------------------------------------------------
--------------------------------------------------------------------------------
----------Curso Básico de Procesamiento de Imágenes y Visión Artificial---------
----------Febrero 2022----------------------------------------------------------
--------------------------------------------------------------------------------
"""

# ------------------------------------------------------------------------------
# 1. Importación de las librerías utilizadas -----------------------------------
# ------------------------------------------------------------------------------

import pygame 
import os
import cv2
import numpy as np

# ------------------------------------------------------------------------------
# 2. Inicialización de la cámara -----------------------------------------------
# ------------------------------------------------------------------------------

cap = cv2.VideoCapture(0)	# Abre el archivo de video para capturar con la cámara
width = int(cap.get(3))	# Variable con el ancho de la imagen capturada por la cámara
height = int(cap.get(4))	# Variable con el alto de la imagen capturada por la cámara

# ------------------------------------------------------------------------------
# 3. Inicialización de las variables del sistema -------------------------------
# ------------------------------------------------------------------------------

# Inicializa la fuente para los textos
pygame.font.init()

# Variables para generar la ventana del juego
SCALE_WIDTH = 1.0	# Factor de escala para incrementar el ancho de la ventana de juego
SCALE_HEIGHT = 1.0	# Factor de escala para incrementar el alto de la ventana de juego
WIDTH = int(width * SCALE_WIDTH)	# Define el ancho de la ventana de juego
HEIGHT = int(height * SCALE_HEIGHT)	# Define el alto de la ventana de juego
WIN = pygame.display.set_mode((WIDTH, HEIGHT))	# Crea la ventana principal del juego
pygame.display.set_caption("Batalla Espacial")	# Titulo del juego
FPS = 60	# Establece la tasa máxima de refreso del juego

# Variables para especificar el texto
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)	# Texto que indica la vida de los participantes
WINNER_FONT = pygame.font.SysFont('comicsans', 70)	# Texto que indica el ganador del juego

# Variables para especificar colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Variables para las interacciones de los jugadores
SPACESHIP_WIDTH = 55	# Ancho de la nave espacial
SPACESHIP_HEIGHT = 40	# Alto de la nave espacial
BULLET_VEL = 25	# Velocidad de los proyectiles disparados
MAX_BULLETS = 1 # Cantidad de proyectiles simultaneamente disparados por una nave

# Variables para el posicionamiento de los jugadores
x_yellow = 0	# Posición del centroide para controlar el movimiento horizontal de la nave amarilla
y_yellow = 0	# Posición del centroide para controlar el movimiento vertical de la nave amarilla
x_red = 0	# Posición del centroide para controlar el movimiento horizontal de la nave roja
y_red = 0	# Posición del centroide para controlar el movimiento vertical  de la nave roja
area_yellow = 0 # Área de la nave amarilla
area_red = 0 # Área de la nave roja

# Variables para los eventos de las colisiones
YELLOW_HIT = pygame.USEREVENT + 1	# Evento que identifica un impacto contra la nave amarilla
RED_HIT = pygame.USEREVENT + 2	# Evento que identifica un impacto contra la nave roja

# Variables para cargar las imágenes en la ventana del juego
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Images', 'spaceship_yellow.png'))	# Nave amarilla
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90) # Cambia el tamaño de la nave amarilla

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Images', 'spaceship_red.png'))	# Nave roja
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)	# Cambia el tamaño de la nave roja

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'space.jpg')), (WIDTH, HEIGHT))	# Imagen con el fondo del juego
GAME_OVER = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'game_over.png')), (WIDTH, HEIGHT)) # Imagen de inicio del juego
GAME_ON = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'game_on.png')), (WIDTH, HEIGHT))	# Imagen de juego terminado

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)	# Dibuja un borde para dividir la zona de juego de las dos naves

# Estructura para el tratamiento morfológico de las imágenes
kernel = np.ones((5, 5), np.uint8)	# Estructura cuadrada para realizar el proceso de dilatación


# ------------------------------------------------------------------------------
# 4. Funciones para controlar la jugabilidad -----------------------------------
# ------------------------------------------------------------------------------


def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
	"""	Dibuja los objetos (imagen de fondo, texto, naves espaciales, proyectiles) que componen el juego en su ventana 
	principal usando las propiedades de Pygame.	Los objetos se actualizan en su posición de acuerdo a la tasa de refresco definida.
	"""
	# Dibuja la imagen de fondo
	WIN.blit(SPACE,(0, 0))
	pygame.draw.rect(WIN, BLACK, BORDER)
	
	# Dibuja los textos que indican la vida de ambos jugadores
	red_health_text = HEALTH_FONT.render("Salud: " + str(red_health), 1, WHITE)
	yellow_health_text = HEALTH_FONT.render("Salud: " + str(yellow_health), 1, WHITE)
	WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
	WIN.blit(yellow_health_text, (10, 10))

	# Dibuja las naves espaciales
	WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
	WIN.blit(RED_SPACESHIP, (red.x, red.y))

	# Dibuja los proyectiles disparados por la nave roja
	for bullet in red_bullets:
		pygame.draw.rect(WIN, RED, bullet)
	
	# Dibuja los proyectiles disparados por la nave amarilla
	for bullet in yellow_bullets:
		pygame.draw.rect(WIN, YELLOW, bullet)

	pygame.display.update()	# Actualiza la imagen en la ventana de juego


def yellow_handle_movement(yellow, x_yellow, y_yellow):
	"""	Controla el movimiento y la posición de la nave amarilla. Recibe como parametros el rectangulo que representa la nave
	y las coordenadas horizontal y vertical del centroide correspondiente al objeto de color amarilla que es identificado 
	por la cámara. Se asigna los valores de coordenadas del centroide a la nave para su movimiento.
	"""

	# Establece los límites horizontales donde la nave puede moverse
	if ((x_yellow > 0) and (x_yellow < BORDER.x - BORDER.width - yellow.width//2)):
		yellow.x = int(x_yellow * SCALE_WIDTH)

	# Establece los límites verticales donde la nave puede moverse
	if ((y_yellow + yellow.height > 0) and (y_yellow < HEIGHT - yellow.height - 10)):
		if ((x_yellow > 0) and (x_yellow < BORDER.x - BORDER.width - yellow.width//2)):
			yellow.y = int(y_yellow * SCALE_HEIGHT)


def red_handle_movement(red, x_red, y_red):
	"""	Controla el movimiento y la posición de la nave roja. Recibe como parametros el rectangulo que representa la nave
	y las coordenadas horizontal y vertical del centroide correspondiente al objeto de color rojo que es identificado 
	por la cámara y se asigna dichos parametros al rectangulo que representa esta nave.
	"""

	# Establece los límites horizontales donde la nave puede moverse
	if ((x_red > BORDER.x + BORDER.width) and (x_red < WIDTH - red.width//2)):
		red.x = int(x_red * SCALE_WIDTH)

	# Establece los límites verticales donde la nave puede moverse
	if ((y_red + red.height > 0) and (y_red < HEIGHT - red.height - 10)):
		if ((x_red > BORDER.x + BORDER.width) and (x_red < WIDTH - red.width//2)):
			red.y = int(y_red * SCALE_HEIGHT)


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
	"""	Controla el estado de los proyectiles disparados por las naves. Recibe como entrada una lista con los
	proyectiles activos dentro de la ventana y de esta forma revisa cuando los proyectiles pueden ser eliminados de la ventana.
	Los proyectiles se eliminan cuando chocan con una nave o salen del recuadro de juego.
	"""

	# Remueve los proyectiles cuando chocan contra la nave roja o si salen de la ventana de juego
	for bullet in yellow_bullets:
		bullet.x += BULLET_VEL
		if red.colliderect(bullet):	# Revisa si hay una colisión para generar un evento
			pygame.event.post(pygame.event.Event(RED_HIT))	# Decrementa la salud de la nave roja
			yellow_bullets.remove(bullet)
		elif bullet.x > WIDTH:
			yellow_bullets.remove(bullet)

	# Remueve los proyectiles cuando chocan contra la nave amarilla o si salen de la ventana de juego
	for bullet in red_bullets:
		bullet.x -= BULLET_VEL
		if yellow.colliderect(bullet):	# Revisa si hay una colisión
			pygame.event.post(pygame.event.Event(YELLOW_HIT))	# Decrementa la salud de la nave amarilla
			red_bullets.remove(bullet)
		elif bullet.x < 0:
			red_bullets.remove(bullet)


def draw_winner(text):
	""" Dibuja un texto en la ventana de juego cuando uno de los dos jugadores ha ganado la partida.
	"""

	draw_text = WINNER_FONT.render(text, 1, WHITE)
	WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, HEIGHT/2 - draw_text.get_height()/2))

	pygame.display.update()	# Actualiza la ventana de juego con el ganador
	pygame.time.delay(3000)	# Pausa la vetanan de juego por tres segundos


def init_window():
	""" Muestra la imagen con la ventana inicial del juego. Indica las directrices para iniciar a jugar.
	"""

	WIN.blit(GAME_ON, (0, 0)) # Dibuja la imagen del inicio de juego
	pygame.display.update()	# Actualiza la ventana

	# Cuando no se ha iniciado el juego espera que se oprima la tecla espacio para iniciar la partida
	game_off = True
	while game_off:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:	# Inicia la partida
					game_off = False


def game_over():
	""" Muestra la imagen con la ventana de juego terminado. Incluye directrices para reiniciar o finalizar el juego.
	"""

	state = False
	WIN.blit(GAME_OVER, (0, 0)) # Dibuja la imagen de fin de juego
	pygame.display.update()	# Actualiza la ventana

	# Espera instrucciones para terminar o reiniciar el juego
	over = True
	while over:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:	# La tecla espacio reinicia el juego y lo lleva a la ventana de inicio
					over = False
					state = True
				elif event.key == pygame.K_ESCAPE:	# La tecla escape finaliza la ejecución del programa (juego)
					over = False
				else:
					pass

	return state


# ------------------------------------------------------------------------------
# 5. Función principal del juego -----------------------------------------------
# ------------------------------------------------------------------------------


def main():

	# Inicializa las componentes del juego
	pygame.init()
	# Inicializa el reloj
	clock = pygame.time.Clock()

	# Dibjua los objectos del juego en la ventana principal
	init_window()

	# Crea los objetos que representan las naves roja y amarilla
	red = pygame.Rect(580, 60, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
	yellow = pygame.Rect(60, 420, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

	# Listas que almacenan los proyectiles activos
	red_bullets = []
	yellow_bullets = []

	# Nivel de vida de las naves
	red_health = 12
	yellow_health = 12

	# Establece las posiciones iniciales de las naves
	x_yellow = 60	# Posición inicial de la nave amarilla en el eje x
	y_yellow = 420	# Posición inicial de la nave amarilla en el eje y
	x_red = 580	# Posición inicial de la nave roja en el eje x
	y_red = 60	# Posición inicial de la nave roja en el eje y

	winner_text = ""	# Variable que almacena la identificación del ganador


	# ------------------------------------------------------------------------------
	# 6. Ciclo principal del juego -------------------------------------------------
	# ------------------------------------------------------------------------------

	game_active = True	# Variable que controla cuando el juego se encuentra activo
	while game_active:

		# ------------------------------------------------------------------------------
		# 7. Captura de video por parte de la cámara -----------------------------------
		# ------------------------------------------------------------------------------

		ret, frame = cap.read()	# Captura de un pantallazo con la cámara
		frame = cv2.flip(frame, 1)	# Elimina el efecto espejo de la imagen capturada
	
		# ------------------------------------------------------------------------------
		# 8. Identificación y seguimiento de objetos con la cámara ---------------------
		# ------------------------------------------------------------------------------

		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)	# Convierte la captura de la cámara del espacio RGB al espacio HSV
			
		low_red = np.array([165 ,95, 180])	# límite inferior para capturar el color rojo en el espacio HSV
		high_red = np.array([200, 200, 250])	# límite superior para capturar el color rojo en el espacio HSV

		low_yellow = np.array([20, 100, 180])# límite inferior para capturar el color amarilla en el espacio HSV
		high_yellow = np.array([40, 255, 255])# límite superior para capturar el color amarilla en el espacio HSV

		red_mask = cv2.inRange(hsv, low_red, high_red)	# Máscara que identifica el rango de color rojo especificado - Binariza
		red_mask = cv2.dilate(red_mask, kernel, iterations = 2)	# Dilata la imagen binarizada con una estructura cuadrada
		red_mask = cv2.GaussianBlur(red_mask,(5, 5), 100)	# Elimina el ruido de los objetos rojos identificados

		yellow_mask = cv2.inRange(hsv, low_yellow, high_yellow)	# Máscara que identifica el rango de color amarilla especificado - Binariza
		yellow_mask = cv2.dilate(yellow_mask, kernel, iterations = 2)	# Dilata la imagen binarizada con una estructura cuadrada
		yellow_mask = cv2.GaussianBlur(yellow_mask, (5, 5), 100)	# Elimina el ruido de los objetos amarillas identificados

		contours_yellow, hierarchy1 = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)	# Obtiene los contornos de los objetos rojos
		
		# Obtiene el objeto de mayor área para controlar la nave roja
		if len(contours_yellow) != 0:
			cnt1 = max(contours_yellow, key=lambda x: cv2.contourArea(x)) # Identifica el objeto rojo de mayor tamaño
			area_red = cv2.contourArea(cnt1)	# Calcula el área del objeto 
			if area_red > 1000:	# Umbral mínimo del objeto que mueve la nave roja
				M1 = cv2.moments(cnt1)	# Obtiene los momentos del objeto
	
				# Evita división por cero cuando no hay objeto detectado
				if M1["m00"] == 0:
					M1["m00"] = 1

				# Obtiene el centroide del objeto rojo detectado
				x_red = int(M1["m10"]/M1["m00"]) # Coordenada del eje x objeto rojo
				y_red = int(M1["m01"]/M1["m00"]) # Coordenada del eje y objeto rojo

				cv2.circle(frame, (x_red, y_red), 5, (255, 0, 0), 2)	# Dibuja un circulo en el centroide del objeto rojo

			cv2.drawContours(frame, cnt1, -1, (0, 0, 255), 1)	# Dibuja los contornos de los objetos detectado en el rango rojo HSV


		contours_red, hierarchy2 = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)	# Obtiene los contornos de los objetos amarillos

		# Obtiene el objeto de mayor área para controlar la nave amarilla
		if len(contours_red) != 0:
			cnt2 = max(contours_red, key=lambda x: cv2.contourArea(x))	# Identifica el objeto amarillo de mayor tamaño
			area_yellow = cv2.contourArea(cnt2)	# Calcula el área del objeto
			if area_yellow > 1000:	# Umbral mínimo del objeto que mueve la nave amarilla
				M2 = cv2.moments(cnt2)

				# Evita división por cero cuando no hay objeto detectado
				if M2["m00"] == 0:
					M2["m00"] == 1

				# Obtiene el centroide del objeto amarillo detectado
				x_yellow = int(M2["m10"]/M2["m00"]) # Coordenada del eje x objeto amarilla
				y_yellow = int(M2["m01"]/M2["m00"]) # Coordenada del eje y objeto amarilla

				cv2.circle(frame, (x_yellow, y_yellow), 5, (255, 0, 0), 2)	# Dibuja un circulo en el centroide del objeto amarilla
		
			cv2.drawContours(frame, cnt2, -1, (0, 0, 255), 1)	# Dibuja los contornos de los objetos detectados en el rango amarilla HSV

		# ------------------------------------------------------------------------------
		# 9. Eventos que controlan las interacciones en el juego -----------------------
		# ------------------------------------------------------------------------------

		# Itera sobre los eventos de pygame que permiten realizar una acción sobre la jugabilidad
		for event in pygame.event.get():
			# Evento para cerrar el juego 
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()	

			# Evento que se activa cuando un proyectil colisiona con la nave roja
			if event.type == RED_HIT:
				red_health-=1

			# Evento que se activa cuando un proyectil colisiona con la nave amarilla
			if event.type == YELLOW_HIT:
				yellow_health-=1

			# Evento que se activa para terminar el juego
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:	# Termina el juego cuando se oprime la tecla q
					game_active = False
	
		
		clock.tick(FPS) # Establece la tasa del reloj que controla el juego

		# ------------------------------------------------------------------------------
		# 10. Creación de los proyectiles que disparan las naves espaciales ------------
		# ------------------------------------------------------------------------------

		if len(yellow_bullets) < MAX_BULLETS:	# Umbral de proyectiles activos disparados por la nave amarilla
			bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 -2, 15, 10)	# Crea un objeto para los proyectiles de la nave amarilla
			yellow_bullets.append(bullet)	# Almacena los objetos de los proyectiles amarillos en una lista

		if len(red_bullets) < MAX_BULLETS:	# Umbral de proyectiles activos disparados por la nave roja
			bullet = pygame.Rect(red.x, red.y + red.height//2 -2, 15, 10)	# Crea un objeto para los proyectiles de la nave roja
			red_bullets.append(bullet)	# Almacena los objetos de los proyectiles rojos en una lista
 
		
		# Revisa si la vida de la nave roja ha llegado a cero
		if red_health <= 0:
			winner_text = "¡GANADOR AMARILLO!"	# Declara al jugador de la nave amarilla como el ganador
	
		# Revisa si la vida de la nave amarilla ha llegado a cero
		if yellow_health <= 0:
			winner_text = "¡GANADOR ROJO!"	# Declara al jugador de la nave roja como el ganador

		# Revisa si el juego ha terminado
		if winner_text != "":
			draw_winner(winner_text) # Función que dibuja en la ventana principal el ganador de la partida
			game_active = False	# Termina el ciclo del juego
			break

		# ------------------------------------------------------------------------------
		# 11. Control de la posición y movimiento de los objetos en el juego -----------
		# ------------------------------------------------------------------------------

		yellow_handle_movement(yellow, x_yellow, y_yellow)	# Función que controla la posición de la nave amarilla
		red_handle_movement(red, x_red, y_red)	# Función que controla la posición de la nave roja
		handle_bullets(yellow_bullets, red_bullets, yellow, red)	# Función que controla el estado de los proyectiles disparados por las naves

		draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)	# Función que dibuja los objetos en la ventana de juego

		# ------------------------------------------------------------------------------
		# 12. Ventana con la captura de la cámara del computador -----------------------
		# ------------------------------------------------------------------------------

		frame = cv2.line(frame, (640//2-1, 0), (640//2-1, HEIGHT), (0, 0, 0), 2)	# Dibuja una linea en el marco de la imagen capturada
		cv2.imshow("frame", frame)	# Muestra la imágen capturada por la cámara

		# Mecanismo para cerrar la ejecución del programa usando openCV
		key = cv2.waitKey(1)
		if key == 27:
			break	
	
	state = game_over()	# Carga la imagen de juego finalizado en la ventana principal

	# Control de las acciones a seguir cuando el juego ha finalizado
	if state == True:
		main()	# Reinicia el juego
	else:
		cap.release()	# Suelta el control del programa sobre la cámara del computador
		cv2.destroyAllWindows()	# Cierra la ventana que muestra la captura de la cámara
		pygame.quit()	# Cierra el juego
		exit()	# Finaliza la ejecución del programa de forma segura


# Función que se ejecuta al iniciar el programa
# Solo habilita la ejecución como un programa principal
if __name__ == "__main__":
	main()			


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
# Importación de las librerias utilizadas --------------------------------------
# ------------------------------------------------------------------------------

import pygame 
import os
import cv2
import numpy as np



# ------------------------------------------------------------------------------
# Inicialización de la camara --------------------------------------------------
# ------------------------------------------------------------------------------

cap = cv2.VideoCapture(0)
width = int(cap.get(3))	# Variable con el ancho de la imagen capturada por la camara
height = int(cap.get(4))	# Variable con el alto de la imagen capturada por la camara

# ------------------------------------------------------------------------------
# Inicialización de las variables del sistema ----------------------------------
# ------------------------------------------------------------------------------

# Inicializa la fuente para los textos
pygame.font.init()

# Variables que generan la ventana del juego
SCALE_WIDTH = 1.0
SCALE_HEIGHT = 1.0
WIDTH = int(width * SCALE_WIDTH)	# Define el ancho de la ventana de juego
HEIGHT = int(height * SCALE_HEIGHT)	# Define el alto de la ventana de juego
WIN = pygame.display.set_mode((WIDTH, HEIGHT))	# Crea la ventana principal del juego
pygame.display.set_caption("Batalla Espacial")
FPS = 60	# Establece la tasa máxmima de refreso del juego

# Variables para especificar el texto
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)	
WINNER_FONT = pygame.font.SysFont('comicsans', 70)

# Variables para especificar colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Variables para las interacciones de los jugadores
SPACESHIP_WIDTH = 55	# Ancho de la nave espacial
SPACESHIP_HEIGHT = 40	# Alto de la nave espacial
BULLET_VEL = 30	# Velocidad de movimiento de los proyectiles
MAX_BULLETS = 1 # Cantidad de proyectiles simultaneamente disparados por una nave

# Variables para el posicionamiento de los jugadores
x_yellow = 0	# Posición del centroide para controlar el movimiento horizontal de la nave verde
y_yellow = 0	# Posición del centroide para controlar el movimiento vertical de la nave verde
x_red = 0	# Posición del centroide para controlar el movimiento horizontal de la nave roja
y_red = 0	# Posición del centroide para controlar el movimiento vertical  de la nave roja
area_yellow = 0 # Área de la nave verde
area_red = 0 # Área de la nave roja

# Variables para los eventos de las colisiones
YELLOW_HIT = pygame.USEREVENT + 1	# Evento que identifica un impacto contra la nave verde
RED_HIT = pygame.USEREVENT + 2	# Evento que identifica un impacto contra la nave roja

# Variables para cargar las imagenes en la ventana del juego
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Images', 'spaceship_yellow.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Images', 'spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'space.jpg')), (WIDTH, HEIGHT))
GAME_OVER = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'game_over.png')), (WIDTH, HEIGHT))
GAME_ON = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'game_on.png')), (WIDTH, HEIGHT))

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)	# Dibuja un borde para dividir la zona de juego de las dos naves

# Estructura para el tratamiento morfologico de las imágenes
kernel = np.ones((5, 5), np.uint8)	# Estructura cuadrada para realizar el proceso de dilatación


# ------------------------------------------------------------------------------
# Funciones para controlar la jugabilidad --------------------------------------
# ------------------------------------------------------------------------------


def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
	"""	Dibuja los objetos (imágen de fondo, texto, naves, proyectiles) que componen el juego en su ventana 
	principal usando las propiedades de Pygame.	Los objetos se actualizan de acuerdo a la tasa de refresco definida.
	"""

	WIN.blit(SPACE,(0, 0))
	pygame.draw.rect(WIN, BLACK, BORDER)

	red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, WHITE)
	yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, WHITE)
	WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
	WIN.blit(yellow_health_text, (10, 10))

	WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
	WIN.blit(RED_SPACESHIP, (red.x, red.y))

	for bullet in red_bullets:
		pygame.draw.rect(WIN, RED, bullet)

	for bullet in yellow_bullets:
		pygame.draw.rect(WIN, YELLOW, bullet)

	pygame.display.update()


def yellow_handle_movement(yellow, x_yellow, y_yellow):
	"""	Controla el movimiento y la posición de la nave verde. Recibe como parametros el rectangulo que represental la nave
	y las coordenadas horizontal y vertical del centroide correspondiente al objeto de color verde que es identificado 
	por la camara y se asigna dichos parametros al rectangulo que representa esta nave.
	"""

	# Establece los limites horizontales donde la nave puede moverse
	if ((x_yellow > 0) and (x_yellow < BORDER.x - BORDER.width - yellow.width//2)):
		yellow.x = int(x_yellow * SCALE_WIDTH)

	# Establece los limites verticales donde la nave puede moverse
	if ((y_yellow + yellow.height > 0) and (y_yellow < HEIGHT - yellow.height - 10)):
		if ((x_yellow > 0) and (x_yellow < BORDER.x - BORDER.width - yellow.width//2)):
			yellow.y = int(y_yellow * SCALE_HEIGHT)


def red_handle_movement(red, x_red, y_red):
	"""	Controla el movimiento y la posición de la nave roja. Recibe como parametros el rectangulo que represental la nave
	y las coordenadas horizontal y vertical del centroide correspondiente al objeto de color rojo que es identificado 
	por la camara y se asigna dichos parametros al rectangulo que representa esta nave.
	"""

	# Establece los limites horizontales donde la nave puede moverse
	if ((x_red > BORDER.x + BORDER.width) and (x_red < WIDTH - red.width//2)):
		red.x = int(x_red * SCALE_WIDTH)

	# Establece los limites verticales donde la nave puede moverse
	if ((y_red + red.height > 0) and (y_red < HEIGHT - red.height - 10)):
		if ((x_red > BORDER.x + BORDER.width) and (x_red < WIDTH - red.width//2)):
			red.y = int(y_red * SCALE_HEIGHT)


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
	"""	Controla el estado de los proyectiles disparados por las naves. Recibe como entrada una lista con los
	proyectiles activos dentro de la ventana y de esta forma revisa cuando los proyectiles pueden ser eliminados de la ventana 
	al chocar contra una de las naves y así generar un evento que decrementa la vida de la nave impactada.
	"""

	# Remueve los proyectiles cuando chocan contra la nave roja si salen de la ventana de juego
	for bullet in yellow_bullets:
		bullet.x += BULLET_VEL
		if red.colliderect(bullet):
			pygame.event.post(pygame.event.Event(RED_HIT))
			yellow_bullets.remove(bullet)
		elif bullet.x > WIDTH:
			yellow_bullets.remove(bullet)

	# Remueve los proyectiles cuando chocan contra la nave verde si salen de la ventana de juego
	for bullet in red_bullets:
		bullet.x -= BULLET_VEL
		if yellow.colliderect(bullet):
			pygame.event.post(pygame.event.Event(YELLOW_HIT))
			red_bullets.remove(bullet)
		elif bullet.x < 0:
			red_bullets.remove(bullet)


def draw_winner(text):
	""" Dibuja un texto en la ventana cuando uno de los dos jugadores ha ganado la partida.
	"""

	draw_text = WINNER_FONT.render(text, 1, WHITE)
	WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, HEIGHT/2 - draw_text.get_height()/2))

	pygame.display.update()
	pygame.time.delay(3000)


def init_window():
	""" Muestra la ventana inicial del juego. Indica las directrices para iniciar a jugar.		
	"""

	WIN.blit(GAME_ON, (0, 0))
	pygame.display.update()

	game_off = True
	while game_off:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					game_off = False


def game_over():
	""" Muestra la ventana de juego terminado. Incluye directrices para reiniciar o finalizar el juego.
	"""

	state = False
	WIN.blit(GAME_OVER, (0, 0))
	pygame.display.update()

	over = True
	while over:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					over = False
					state = True
				elif event.key == pygame.K_ESCAPE:
					over = False
				else:
					pass

	return state


# ------------------------------------------------------------------------------
# Función principal del juego --------------------------------------------------
# ------------------------------------------------------------------------------


def main():

	# Inicializa las componentes del juego
	pygame.init()
	# Inicializa el reloj
	clock = pygame.time.Clock()

	# Dibjua los objectos del juego en la ventana principal
	init_window()

	# Crea los objetos que representan las naves roja y verde
	red = pygame.Rect(580, 60, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
	yellow = pygame.Rect(60, 420, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

	# Listas que almacenan los proyectiles activos
	red_bullets = []
	yellow_bullets = []

	# Nivel de vida de las naves
	red_health = 10
	yellow_health = 10

	# Establece las posiciones iniciales de las naves
	x_yellow = 60	# Posición inicial de la nave verde en el eje x
	y_yellow = 420	# Posición inicial de la nave verde en el eje y
	x_red = 580	# Posición inicial de la nave roja en el eje x
	y_red = 60	# Posición inicial de la nave roja en el eje y

	winner_text = ""	# Variable que almacena la identificación del ganador


	# ------------------------------------------------------------------------------
	# Ciclo principal del juego ----------------------------------------------------
	# ------------------------------------------------------------------------------

	game_active = True	# Variable que controla la actividad del juego
	while game_active:

		# ------------------------------------------------------------------------------
		# Captura de video por parte de la camara --------------------------------------
		# ------------------------------------------------------------------------------

		ret, frame = cap.read()	# Captura de video con la camara
		frame = cv2.flip(frame, 1)	# Elimina el efecto espejo de la imagen capturada
	
		# ------------------------------------------------------------------------------
		# Identificación y seguimiento de objetos con la camara ------------------------
		# ------------------------------------------------------------------------------

		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)	# Convierte la captura de la camara al espacio HSV
			
		low_red = np.array([165 ,95, 180])	# Limite inferior para capturar el color rojo en el espacio HSV
		high_red = np.array([200, 200, 250])	# Limite superior para capturar el color rojo en el espacio HSV

		low_yellow = np.array([20, 100, 180])# Limite inferior para capturar el color verde en el espacio HSV
		high_yellow = np.array([40, 255, 255])# Limite superior para capturar el color verde en el espacio HSV

		red_mask = cv2.inRange(hsv, low_red, high_red)	# Mascara que identifica el rango de color rojo especificado - Binariza
		red_mask = cv2.dilate(red_mask, kernel, iterations = 2)	# Dilata la imagen binarizada con una estructura cuadrada
		red_mask = cv2.GaussianBlur(red_mask,(5, 5), 100)	# Elimina el ruido de los objetos rojos identificados

		yellow_mask = cv2.inRange(hsv, low_yellow, high_yellow)	# Mascara que identifica el rango de color verde especificado - Binariza
		yellow_mask = cv2.dilate(yellow_mask, kernel, iterations = 2)	# Dilata la imagen binarizada con una estructura cuadrada
		yellow_mask = cv2.GaussianBlur(yellow_mask, (5, 5), 100)	# Elimina el ruido de los objetos verdes identificados

		contours_yellow, hierarchy1 = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)	# Obtiene los contornos de los objetos rojos
		
		# Obtiene el objeto de mayor area para controlar la nave roja
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


		contours_red, hierarchy2 = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)	# Obtiene los contornos de los objetos verdes

		# Obtiene el objeto de mayor area para controlar la nave verde
		if len(contours_red) != 0:
			cnt2 = max(contours_red, key=lambda x: cv2.contourArea(x))	# Identifica el objeto verde de mayor tamaño
			area_yellow = cv2.contourArea(cnt2)	# Calcula el área del objeto
			if area_yellow > 1000:	# Umbral mínimo del objeto que mueve la nave verde
				M2 = cv2.moments(cnt2)

				# Evita división por cero cuando no hay objeto detectado
				if M2["m00"] == 0:
					M2["m00"] == 1

				# Obtiene el centroide del objeto verde detectado
				x_yellow = int(M2["m10"]/M2["m00"]) # Coordenada del eje x objeto verde
				y_yellow = int(M2["m01"]/M2["m00"]) # Coordenada del eje y objeto verde

				cv2.circle(frame, (x_yellow, y_yellow), 5, (255, 0, 0), 2)	# Dibuja un circulo en el centroide del objeto verde
		
			cv2.drawContours(frame, cnt2, -1, (0, 0, 255), 1)	# Dibuja los contornos de los objetos detectados en el rango verde HSV

		# ------------------------------------------------------------------------------
		# Eventos que controlan las interacciones en el juego --------------------------
		# ------------------------------------------------------------------------------

		for event in pygame.event.get():
			# Evento para cerrar el juego 
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()	

			# Evento que se activa cuando un proyectil colisiona con la nave roja
			if event.type == RED_HIT:
				red_health-=1

			# Evento que se activa cuando un proyectil colisiona con la nave verde
			if event.type == YELLOW_HIT:
				yellow_health-=1

			# Evento que se activa para terminar el juego
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:	# Termina el juego cuando se oprime la tecla q
					game_active = False
	
		
		clock.tick(FPS) # Establece la tasa del reloj que controla el juego

		# ------------------------------------------------------------------------------
		# Eventos que controlan las interacciones en el juego --------------------------
		# ------------------------------------------------------------------------------

		if len(yellow_bullets) < MAX_BULLETS:	# Umbral de proyectiles activos disparados por la nave verde
			bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 -2, 15, 10)	# Crea un objeto para los proyectiles de la nave verde
			yellow_bullets.append(bullet)	# Almacena los objetos de los proyectiles verdes en una lista

		if len(red_bullets) < MAX_BULLETS:	# Umbral de proyectiles activos disparados por la nave roja
			bullet = pygame.Rect(red.x, red.y + red.height//2 -2, 15, 10)	# Crea un objeto para los proyectiles de la nave roja
			red_bullets.append(bullet)	# Almacena los objetos de los proyectiles rojos en una lista
 
		
		# Revisa si la vida de la nave roja ha llegado a cero
		if red_health <= 0:
			winner_text = "¡GANADOR AMARILLO!"	# Declara al jugador de la nave verde como el ganador
	
		# Revisa si la vida de la nave verde ha llegado a cero
		if yellow_health <= 0:
			winner_text = "¡GANADOR ROJO!"	# Declara al jugador de la nave roja como el ganador

		
		if winner_text != "":
			draw_winner(winner_text) # Función que dibuja en la ventana principal el ganador de la partida
			game_active = False	# Termina el ciclo del juego
			break

		# ------------------------------------------------------------------------------
		# Control de la posición y movimiento de los objetos en el juego ---------------
		# ------------------------------------------------------------------------------

		yellow_handle_movement(yellow, x_yellow, y_yellow)	# Función que controla la posición de la nave verde
		red_handle_movement(red, x_red, y_red)	# Función que controla la posición de la nave roja
		handle_bullets(yellow_bullets, red_bullets, yellow, red)	# Función que controla el estado de los proyectiles disparados por las naves

		draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)	# Función que dibuja los objetos del juego

		# ------------------------------------------------------------------------------
		# Ventana con la captura de la camara del computador ---------------------------
		# ------------------------------------------------------------------------------

		frame = cv2.line(frame, (640//2-1, 0), (640//2-1, HEIGHT), (0, 0, 0), 2)	# Dibuja una linea en el marco de la imágen capturada
		cv2.imshow("frame", frame)	# Muestra la imágen capturada por la camara

		# Mecanismo para cerrar el juego desde las propiedades de openCV
		key = cv2.waitKey(1)
		if key == 27:
			break	
	
	state = game_over()	# Carga la imágen de juego finalizado en la ventana principal

	# Control de las acciones a seguir cuando el juego ha finalizado
	if state == True:
		main()	# Reinicia el juego
	else:
		cap.release()	# Suelta el control del programa sobre la camara del computador
		cv2.destroyAllWindows()	# Cierra la ventana que muestra la captura de la camara
		pygame.quit()	# Cierra el juego
		exit()	# Finaliza la ejecución del programa de forma segura


# Función que se ejecuta al iniciar el programa
# Solo habilita la ejecución como un programa principal
if __name__ == "__main__":
	main()			


PyPassCracker
Herramienta en Python para auditar contraseñas mediante ataques de diccionario y fuerza bruta.

Caracteristicas
Deteccion automatica de hashes MD5, SHA1, SHA224, SHA256, SHA384 y SHA512.
Soporte para procesar un solo hash o listas enteras desde archivos de texto.
Multiprocesamiento para acelerar los ataques de fuerza bruta.
Fuerza bruta con letras, numeros y caracteres especiales.
Autoguardado de contraseñas encontradas en una base de datos SQLite.

Ejemplos de uso
Ataque de fuerza bruta a un archivo con 8 nucleos y longitud maxima de 4:
python cracker.py -t objetivos.txt -m bruta -c 8 -l 4

Ataque por diccionario a un solo hash:
python cracker.py -t tuhashaca -m diccionario -w diccionario.txt

Parametros
-t : Hash objetivo o ruta del archivo txt con hashes
-m : Modo de ataque (bruta o diccionario)
-w : Ruta del archivo de diccionario
-l : Longitud maxima para fuerza bruta
-c : Cantidad de nucleos a usar
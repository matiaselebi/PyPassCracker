import argparse
import hashlib
import itertools
import string
import multiprocessing
import time
import os

def mostrar_banner():
    print("======================================")
    print("           PyPassCracker              ")
    print("======================================")

def detectar_algoritmo(hash_objetivo):
    longitud = len(hash_objetivo)
    if longitud == 32: return "md5"
    elif longitud == 40: return "sha1"
    elif longitud == 56: return "sha224"
    elif longitud == 64: return "sha256"
    elif longitud == 96: return "sha384"
    elif longitud == 128: return "sha512"
    return None

def cifrar(texto, algoritmo):
    if algoritmo == "md5": return hashlib.md5(texto.encode()).hexdigest()
    elif algoritmo == "sha1": return hashlib.sha1(texto.encode()).hexdigest()
    elif algoritmo == "sha224": return hashlib.sha224(texto.encode()).hexdigest()
    elif algoritmo == "sha256": return hashlib.sha256(texto.encode()).hexdigest()
    elif algoritmo == "sha384": return hashlib.sha384(texto.encode()).hexdigest()
    elif algoritmo == "sha512": return hashlib.sha512(texto.encode()).hexdigest()
    return None

def ataque_diccionario(hash_objetivo, ruta_diccionario, algoritmo):
    inicio = time.time()
    intentos = 0
    try:
        with open(ruta_diccionario, "r", encoding="utf-8", errors="ignore") as archivo:
            for linea in archivo:
                intentos += 1
                palabra = linea.strip()
                if cifrar(palabra, algoritmo) == hash_objetivo:
                    fin = time.time()
                    print(f"\nExito: La contraseña es {palabra}")
                    print(f"Intentos: {intentos} | Tiempo: {fin - inicio:.2f} segundos")
                    return True
        print("Fallo: No se encontro la contraseña.")
        return False
    except FileNotFoundError:
        print("Error: No se encontro el archivo.")
        return False

def worker_fuerza_bruta(hash_objetivo, longitud, caracteres, subconjunto, resultado_encontrado, contador_intentos, algoritmo):
    for prefijo in subconjunto:
        if resultado_encontrado.is_set(): return
        for resto in itertools.product(caracteres, repeat=longitud - 1):
            if resultado_encontrado.is_set(): return
            palabra = prefijo + ''.join(resto)
            with contador_intentos.get_lock():
                contador_intentos.value += 1
            if cifrar(palabra, algoritmo) == hash_objetivo:
                print(f"\nExito: La contraseña es {palabra}")
                resultado_encontrado.set()
                return

def ataque_fuerza_bruta_paralelo(hash_objetivo, longitud_maxima, num_procesos, algoritmo):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    resultado_encontrado = multiprocessing.Event()
    contador_intentos = multiprocessing.Value('q', 0)
    inicio = time.time()
    
    for longitud in range(1, longitud_maxima + 1):
        if resultado_encontrado.is_set(): break
        print(f"Probando longitud: {longitud}")
        prefijos = list(caracteres)
        chunk_size = max(1, len(prefijos) // num_procesos)
        procesos = []
        for i in range(num_procesos):
            start = i * chunk_size
            end = len(prefijos) if i == num_procesos - 1 else (i + 1) * chunk_size
            subconjunto = prefijos[start:end]
            p = multiprocessing.Process(target=worker_fuerza_bruta, 
                                        args=(hash_objetivo, longitud, caracteres, subconjunto, resultado_encontrado, contador_intentos, algoritmo))
            procesos.append(p)
            p.start()
        for p in procesos: p.join()

    if resultado_encontrado.is_set():
        fin = time.time()
        print(f"Intentos totales: {contador_intentos.value} | Tiempo total: {fin - inicio:.2f} segundos")
    else:
        print("Fallo: No se encontro la contraseña.")

def procesar_hash(hash_objetivo, mode, wordlist, length, cores):
    print(f"\nAnalizando objetivo: {hash_objetivo}")
    algoritmo = detectar_algoritmo(hash_objetivo)
    
    if not algoritmo:
        print("Error: El hash no parece ser un formato soportado.")
        return

    print(f"Algoritmo detectado: {algoritmo.upper()}")

    if mode == "diccionario":
        ataque_diccionario(hash_objetivo, wordlist, algoritmo)
    else:
        print(f"Modo: Fuerza Bruta | Nucleos: {cores} | Longitud Max: {length}")
        ataque_fuerza_bruta_paralelo(hash_objetivo, length, cores, algoritmo)

def main():
    mostrar_banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-m", "--mode", choices=["diccionario", "bruta"], required=True)
    parser.add_argument("-w", "--wordlist")
    parser.add_argument("-l", "--length", type=int, default=4)
    parser.add_argument("-c", "--cores", type=int, default=1)
    
    args = parser.parse_args()

    if os.path.isfile(args.target):
        try:
            with open(args.target, "r") as f:
                hashes = [linea.strip() for linea in f if linea.strip()]
            print(f"Cargados {len(hashes)} hashes desde el archivo.")
            for h in hashes:
                procesar_hash(h, args.mode, args.wordlist, args.length, args.cores)
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
    else:
        procesar_hash(args.target, args.mode, args.wordlist, args.length, args.cores)

if __name__ == "__main__":
    main()
import argparse
import hashlib
import itertools
import string
import multiprocessing
import time

def mostrar_banner():
    print("======================================")
    print("           PyPassCracker              ")
    print("      Parallel Edition (R7)           ")
    print("======================================")

def ataque_diccionario(hash_objetivo, ruta_diccionario):
    inicio = time.time()
    intentos = 0
    try:
        with open(ruta_diccionario, "r", encoding="utf-8", errors="ignore") as archivo:
            for linea in archivo:
                intentos += 1
                palabra = linea.strip()
                if hashlib.md5(palabra.encode()).hexdigest() == hash_objetivo:
                    fin = time.time()
                    print(f"\nExito: La contrasena es {palabra}")
                    print(f"Intentos: {intentos} | Tiempo: {fin - inicio:.2f} segundos")
                    return True
        print("\nFallo: No se encontro la contrasena.")
        return False
    except FileNotFoundError:
        print("\nError: No se encontro el archivo.")
        return False

def worker_fuerza_bruta(hash_objetivo, longitud, caracteres, subconjunto, resultado_encontrado, contador_intentos):
    for prefijo in subconjunto:
        if resultado_encontrado.is_set(): return
        for resto in itertools.product(caracteres, repeat=longitud - 1):
            if resultado_encontrado.is_set(): return
            palabra = prefijo + ''.join(resto)
            
            # Incremento seguro del contador
            with contador_intentos.get_lock():
                contador_intentos.value += 1
                
            if hashlib.md5(palabra.encode()).hexdigest() == hash_objetivo:
                print(f"\nExito: La contrasena es {palabra}")
                resultado_encontrado.set()
                return

def ataque_fuerza_bruta_paralelo(hash_objetivo, longitud_maxima, num_procesos):
    caracteres = string.ascii_letters + string.digits
    resultado_encontrado = multiprocessing.Event()
    contador_intentos = multiprocessing.Value('q', 0) # 'q' para soportar números más grandes (long long)
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
                                        args=(hash_objetivo, longitud, caracteres, subconjunto, resultado_encontrado, contador_intentos))
            procesos.append(p)
            p.start()
        for p in procesos: p.join()

    if resultado_encontrado.is_set():
        fin = time.time()
        print(f"Intentos totales: {contador_intentos.value} | Tiempo total: {fin - inicio:.2f} segundos")
    else:
        print("\nFallo: No se encontro la contrasena.")

def main():
    mostrar_banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-m", "--mode", choices=["diccionario", "bruta"], required=True)
    parser.add_argument("-w", "--wordlist")
    parser.add_argument("-l", "--length", type=int, default=4)
    parser.add_argument("-c", "--cores", type=int, default=1)
    
    args = parser.parse_args()
    
    if args.mode == "diccionario":
        print(f"Modo: Diccionario | Archivo: {args.wordlist}")
        ataque_diccionario(args.target, args.wordlist)
    else:
        print(f"Modo: Fuerza Bruta | Nucleos: {args.cores} | Longitud Max: {args.length}")
        ataque_fuerza_bruta_paralelo(args.target, args.length, args.cores)

if __name__ == "__main__":
    main()
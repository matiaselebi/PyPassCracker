import argparse
import hashlib

def mostrar_banner():
    print("======================================")
    print("           PyPassCracker              ")
    print("======================================")

def ataque_diccionario(hash_objetivo, ruta_diccionario):
    try:
        with open(ruta_diccionario, "r", encoding="utf-8", errors="ignore") as archivo:
            for linea in archivo:
                palabra = linea.strip()
                hash_palabra = hashlib.md5(palabra.encode()).hexdigest()
                if hash_palabra == hash_objetivo:
                    print(f"Exito: La contraseña es {palabra}")
                    return True
        print("Fallo: No se encontro la contraseña en el diccionario.")
        return False
    except FileNotFoundError:
        print("Error: No se encontro el archivo del diccionario.")
        return False

def main():
    mostrar_banner()
    parser = argparse.ArgumentParser(description="Herramienta para auditar contraseñas")
    parser.add_argument("-t", "--target", required=True, help="El hash MD5 que queremos romper")
    parser.add_argument("-m", "--mode", choices=["diccionario", "bruta"], required=True, help="El modo de ataque a usar")
    parser.add_argument("-w", "--wordlist", help="Ruta al archivo de diccionario")
    
    args = parser.parse_args()

    if args.mode == "diccionario":
        if not args.wordlist:
            print("Error: Para el modo diccionario necesitas indicar un archivo con -w")
            return
        print(f"Iniciando ataque por diccionario al hash: {args.target}")
        ataque_diccionario(args.target, args.wordlist)
    elif args.mode == "bruta":
        print("Aca vamos a programar la generacion de caracteres")

if __name__ == "__main__":
    main()
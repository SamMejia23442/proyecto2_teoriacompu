# main.py
import sys
import os
from gramatica import construir_gramatica_proyecto2
from pda import gramatica_a_pda, mostrar_definicion_pda, simular_pda, formatear_resultado_pda
from cyk import algoritmo_cyk, formatear_resultado_cyk
from analisis_crecimiento import ejecutar_analisis_crecimiento, formatear_tabla_crecimiento


def leer_archivo(ruta):
    # lee todas las lineas del archivo de texto, ignorando vacias y comentarios
    if not os.path.exists(ruta):
        print(f"El archivo '{ruta}' no existe.")
        return []
    with open(ruta, 'r', encoding='utf-8') as f:
        lineas = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
        return lineas


def evaluar_frase(gramatica, pda, frase, mostrar_detalle=True):
    # ejecuta tanto el PDA como el algoritmo CYK sobre la frase dada y compara resultados
    res_pda = simular_pda(pda, frase)
    res_cyk = algoritmo_cyk(gramatica, frase)

    if mostrar_detalle:
        print("\n" + formatear_resultado_pda(res_pda))
        print("\n" + formatear_resultado_cyk(res_cyk))

    print("\n" + "-" * 78)
    print(f"RESUMEN COMPARATIVO PARA: \"{frase}\" (n = {res_cyk['n']} palabras)")
    print("-" * 78)
    est_pda = "ACEPTADA" if res_pda['aceptada'] else "RECHAZADA"
    est_cyk = "ACEPTADA" if res_cyk['aceptada'] else "RECHAZADA"
    print(f"  * Reconocimiento con PDA : {est_pda:<10} | Operaciones: {res_pda['operaciones']:>8,} | Configs exploradas: {res_pda['configuraciones_exploradas']}")
    print(f"  * Reconocimiento con CYK : {est_cyk:<10} | Operaciones: {res_cyk['operaciones']:>8,} | Reglas evaluadas:   {res_cyk['evaluaciones_reglas']}")
    if res_cyk['operaciones'] > 0:
        razon = res_pda['operaciones'] / res_cyk['operaciones']
        print(f"  * Relacion de operaciones (PDA / CYK): {razon:.2f}x")
    print("-" * 78)

    return res_pda, res_cyk


def menu():
    print("\n============================================================")
    print("   PROYECTO #2 - RECONOCIMIENTO DE CADENAS (PDA y CYK)")
    print("============================================================")
    print("1. Ingresar frase manualmente (evaluar con PDA y CYK)")
    print("2. Cargar y evaluar frases desde archivo (ej. frases_prueba.txt)")
    print("3. Ver gramatica G y definicion formal del PDA convertido")
    print("4. Ejecutar analisis de tasa de crecimiento (CYK vs. PDA)")
    print("5. Salir")
    return input("Elige una opcion: ").strip()


def main():
    gramatica = construir_gramatica_proyecto2()
    pda = gramatica_a_pda(gramatica)

    # permite ejecucion directa pasando la frase como argumento en consola
    if len(sys.argv) > 1:
        frase_arg = " ".join(sys.argv[1:])
        evaluar_frase(gramatica, pda, frase_arg, mostrar_detalle=True)
        return

    while True:
        opcion = menu()

        if opcion == '1':
            frase = input("\nEscribe la frase en ingles a reconocer (ej. 'she eats a cake with a fork'): ").strip()
            if frase:
                evaluar_frase(gramatica, pda, frase, mostrar_detalle=True)
            else:
                print("No se ingreso ninguna frase.")

        elif opcion == '2':
            ruta = input("\nEscribe el nombre del archivo (Enter para 'frases_prueba.txt'): ").strip()
            if not ruta:
                ruta = "frases_prueba.txt"
            frases = leer_archivo(ruta)
            if frases:
                ver_pasos = input("¿Mostrar registro completo de pasos de cada frase? (s/n, Enter=s): ").strip().lower()
                mostrar_det = (ver_pasos != 'n')
                for idx, frase in enumerate(frases, 1):
                    print(f"\n>>> Frase #{idx} de {len(frases)} <<<")
                    evaluar_frase(gramatica, pda, frase, mostrar_detalle=mostrar_det)

        elif opcion == '3':
            print("\n" + "=" * 78)
            print(gramatica.mostrar_gramatica())
            print("=" * 78)
            print(mostrar_definicion_pda(pda))
            print("=" * 78)

        elif opcion == '4':
            resultados_ac, resultados_re = ejecutar_analisis_crecimiento(generar_grafica=True)
            print("\n" + formatear_tabla_crecimiento(resultados_ac, resultados_re))
            if os.path.exists("grafica_crecimiento.png"):
                print("\n[OK] Grafica guardada en 'grafica_crecimiento.png'.")

        elif opcion == '5':
            print("Saliendo del programa...")
            sys.exit(0)

        else:
            print("Opcion invalida, intenta de nuevo.")


if __name__ == '__main__':
    main()

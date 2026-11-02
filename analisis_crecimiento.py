# analisis_crecimiento.py
import os
from gramatica import construir_gramatica_proyecto2
from pda import gramatica_a_pda, simular_pda
from cyk import algoritmo_cyk, calcular_operaciones_teoricas_cyk


# conjunto de frases validas de longitud creciente n para evaluar tasa de crecimiento
CASOS_CRECIMIENTO = [
    (2, "she eats"),
    (3, "the cat drinks"),
    (4, "she eats a cake"),
    (5, "the dog eats the meat"),
    (6, "the cat drinks in the oven"),
    (7, "she eats a cake with a fork"),
    (8, "the cat eats the soup with a spoon"),
    (9, "the cat drinks with a spoon in the oven"),
    (10, "she cuts the meat with a knife in the oven"),
    (11, "the dog eats a cake with a fork in the oven"),
    (12, "the cat drinks with a spoon in the oven with a fork"),
    (13, "he cooks the soup with a spoon in the oven with a fork"),
    (14, "the cat cuts the meat with a knife in the oven with a fork"),
    (16, "she eats the cake with a fork in the oven with a spoon in the oven"),
]

# casos adicionales de rechazo para comparar comportamiento en el peor caso (busqueda exhaustiva)
CASOS_RECHAZO = [
    (3, "cat the eats"),
    (6, "she drinks juice with a spoon"),
    (9, "she cuts a cake with a knife in oven"),
    (12, "the dog eats the meat with a fork in the cat with"),
]


def ejecutar_analisis_crecimiento(generar_grafica=True):
    gramatica = construir_gramatica_proyecto2()
    pda = gramatica_a_pda(gramatica)

    resultados = []
    for _, frase in CASOS_CRECIMIENTO:
        res_cyk = algoritmo_cyk(gramatica, frase)
        res_pda = simular_pda(pda, frase)
        ops_teo_cyk = calcular_operaciones_teoricas_cyk(res_cyk['n'])

        resultados.append({
            'n': res_cyk['n'],
            'frase': frase,
            'aceptada': res_cyk['aceptada'],
            'ops_cyk': res_cyk['operaciones'],
            'ops_cyk_teorico': ops_teo_cyk,
            'reglas_cyk': res_cyk['evaluaciones_reglas'],
            'ops_pda': res_pda['operaciones'],
            'configs_pda': res_pda['configuraciones_exploradas'],
            'razon_pda_cyk': res_pda['operaciones'] / res_cyk['operaciones']
        })

    resultados_rechazo = []
    for _, frase in CASOS_RECHAZO:
        res_cyk = algoritmo_cyk(gramatica, frase)
        res_pda = simular_pda(pda, frase)
        ops_teo_cyk = calcular_operaciones_teoricas_cyk(res_cyk['n'])

        resultados_rechazo.append({
            'n': res_cyk['n'],
            'frase': frase,
            'aceptada': res_cyk['aceptada'],
            'ops_cyk': res_cyk['operaciones'],
            'ops_cyk_teorico': ops_teo_cyk,
            'reglas_cyk': res_cyk['evaluaciones_reglas'],
            'ops_pda': res_pda['operaciones'],
            'configs_pda': res_pda['configuraciones_exploradas'],
            'razon_pda_cyk': res_pda['operaciones'] / res_cyk['operaciones']
        })

    if generar_grafica:
        generar_grafica_comparativa(resultados, resultados_rechazo)

    return resultados, resultados_rechazo


def generar_grafica_comparativa(resultados, resultados_rechazo=None, ruta_salida="grafica_crecimiento.png"):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    ns = [r['n'] for r in resultados]
    ops_cyk = [r['ops_cyk'] for r in resultados]
    ops_pda = [r['ops_pda'] for r in resultados]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    # Subplot 1: Escala lineal
    ax1.plot(ns, ops_cyk, marker='o', linewidth=2.2, color='#1f77b4', label='Algoritmo CYK — Θ(n³)')
    ax1.plot(ns, ops_pda, marker='s', linewidth=2.2, color='#d62728', label='PDA (Aceptadas) — Backtracking')
    if resultados_rechazo:
        ns_r = [r['n'] for r in resultados_rechazo]
        ops_pda_r = [r['ops_pda'] for r in resultados_rechazo]
        ax1.plot(ns_r, ops_pda_r, marker='^', linestyle='--', linewidth=1.8, color='#ff7f0e', label='PDA (Rechazadas — Búsqueda exhaustiva)')
    ax1.set_title('Conteo de Operaciones vs. Longitud n (Escala Lineal)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Longitud de la cadena n (número de palabras)', fontsize=10)
    ax1.set_ylabel('Número de operaciones elementales', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(fontsize=9)

    # Subplot 2: Escala semilogaritmica (eje Y en log)
    ax2.plot(ns, ops_cyk, marker='o', linewidth=2.2, color='#1f77b4', label='Algoritmo CYK — Θ(n³)')
    ax2.plot(ns, ops_pda, marker='s', linewidth=2.2, color='#d62728', label='PDA (Aceptadas)')
    if resultados_rechazo:
        ns_r = [r['n'] for r in resultados_rechazo]
        ops_pda_r = [r['ops_pda'] for r in resultados_rechazo]
        ax2.plot(ns_r, ops_pda_r, marker='^', linestyle='--', linewidth=1.8, color='#ff7f0e', label='PDA (Rechazadas)')
    ax2.set_yscale('log')
    ax2.set_title('Conteo de Operaciones vs. Longitud n (Escala Logarítmica)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Longitud de la cadena n (número de palabras)', fontsize=10)
    ax2.set_ylabel('Operaciones elementales (escala log)', fontsize=10)
    ax2.grid(True, which='both', linestyle='--', alpha=0.6)
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=220)
    plt.close(fig)
    return os.path.exists(ruta_salida)


def formatear_tabla_crecimiento(resultados, resultados_rechazo=None):
    lineas = []
    lineas.append("=" * 100)
    lineas.append("ANALISIS DE TASA DE CRECIMIENTO Y CONTEO DE OPERACIONES (CYK vs. PDA)")
    lineas.append("=" * 100)
    lineas.append(" Expresiones Analiticas y Notacion Asintotica:")
    lineas.append("  * Algoritmo CYK:  T_CYK(n) = (11/3)n^3 + n^2 + (148/3)n   =>  Tasa asintotica: Theta(n^3)")
    lineas.append("    - Evaluaciones de producciones: R_CYK(n) = (5/6)(n^3 - n) + 25n")
    lineas.append("  * Automatas de Pila (PDA no determinista):")
    lineas.append("    - Caso general CFG en CNF (backtracking):  T_PDA(n) = O(b^n)  (exponencial)")
    lineas.append("    - Mejor caso (sin retroceso en producciones recursivas): Omega(n)")
    lineas.append("    - En la gramatica G con poda por longitud CNF (k <= n - i): O(n^2) a O(b^n) segun ramificacion")
    lineas.append("-" * 100)
    lineas.append("1. CADENAS ACEPTADAS DE LONGITUD CRECIENTE n:")
    lineas.append("-" * 100)
    encabezado = (
        f"{'n':>3} | {'Estado':^9} | {'Ops CYK':>10} | {'Teorico CYK':>11} | "
        f"{'Ops PDA':>10} | {'Configs PDA':>11} | {'PDA / CYK':>9} | {'Frase'}"
    )
    lineas.append(encabezado)
    lineas.append("-" * 100)

    for r in resultados:
        est = "ACEPTADA" if r['aceptada'] else "RECHAZADA"
        frase_corta = r['frase'] if len(r['frase']) <= 30 else r['frase'][:27] + "..."
        lineas.append(
            f"{r['n']:>3} | {est:^9} | {r['ops_cyk']:>10,} | {r['ops_cyk_teorico']:>11,} | "
            f"{r['ops_pda']:>10,} | {r['configs_pda']:>11,} | {r['razon_pda_cyk']:>8.2f}x | {frase_corta}"
        )

    if resultados_rechazo:
        lineas.append("-" * 100)
        lineas.append("2. CADENAS RECHAZADAS (EXPLORACION EXHAUSTIVA DEL ESPACIO DE BUSQUEDA EN EL PDA):")
        lineas.append("-" * 100)
        for r in resultados_rechazo:
            est = "ACEPTADA" if r['aceptada'] else "RECHAZADA"
            frase_corta = r['frase'] if len(r['frase']) <= 30 else r['frase'][:27] + "..."
            lineas.append(
                f"{r['n']:>3} | {est:^9} | {r['ops_cyk']:>10,} | {r['ops_cyk_teorico']:>11,} | "
                f"{r['ops_pda']:>10,} | {r['configs_pda']:>11,} | {r['razon_pda_cyk']:>8.2f}x | {frase_corta}"
            )

    lineas.append("=" * 100)
    return "\n".join(lineas)


if __name__ == '__main__':
    res_ac, res_re = ejecutar_analisis_crecimiento(generar_grafica=True)
    print(formatear_tabla_crecimiento(res_ac, res_re))

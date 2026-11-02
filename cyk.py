# cyk.py
from gramatica import tokenizar_frase


def reconstruir_pasos_derivacion_cyk(backpointers, i, j, variable):
    # devuelve la lista de producciones (A, cuerpo) en preorden (derivacion por la izquierda)
    info = backpointers[i][j].get(variable, [])
    if not info:
        return []

    primera = info[0]
    if primera[0] == 'terminal':
        palabra = primera[1]
        return [(variable, [palabra])]
    else:
        _, k, b, c = primera
        pasos_izq = reconstruir_pasos_derivacion_cyk(backpointers, i, k, b)
        pasos_der = reconstruir_pasos_derivacion_cyk(backpointers, k + 1, j, c)
        return [(variable, [b, c])] + pasos_izq + pasos_der


def generar_derivacion_izquierda_cyk(backpointers, n, simbolo_inicial='S'):
    # aplica las producciones del arbol de parseo para mostrar cada paso S => ... => w
    producciones = reconstruir_pasos_derivacion_cyk(backpointers, 0, n - 1, simbolo_inicial)
    if not producciones:
        return []

    forma_sentencial = [simbolo_inicial]
    pasos = [simbolo_inicial]
    variables_conocidas = {'S', 'VP', 'PP', 'NP', 'V', 'P', 'N', 'Det'}

    for izq, der in producciones:
        for idx, sim in enumerate(forma_sentencial):
            if sim == izq and sim in variables_conocidas:
                forma_sentencial = forma_sentencial[:idx] + der + forma_sentencial[idx + 1:]
                pasos.append(f"{' '.join(forma_sentencial)}   (usando {izq} -> {' '.join(der)})")
                break

    return pasos


def construir_arbol_ascii(backpointers, i, j, variable, prefijo="", es_ultimo=True):
    # genera una representacion en texto del arbol sintactico obtenido por CYK
    conector = "`-- " if es_ultimo else "|-- "
    info = backpointers[i][j].get(variable, [])
    if not info:
        return [f"{prefijo}{conector}{variable}"]

    primera = info[0]
    if primera[0] == 'terminal':
        palabra = primera[1]
        return [f"{prefijo}{conector}{variable} -> '{palabra}'"]

    _, k, b, c = primera
    lineas = [f"{prefijo}{conector}{variable}"]
    nuevo_prefijo = prefijo + ("    " if es_ultimo else "|   ")
    lineas.extend(construir_arbol_ascii(backpointers, i, k, b, nuevo_prefijo, False))
    lineas.extend(construir_arbol_ascii(backpointers, k + 1, j, c, nuevo_prefijo, True))
    return lineas


def calcular_operaciones_teoricas_cyk(n, num_terminales=25, num_binarias=5):
    # calcula la cantidad exacta de operaciones elementales de CYK en funcion de n:
    # Fase 1 (longitud l = 1): n iteraciones externas * num_terminales evaluaciones
    # Fase 2 (longitud l = 2..n): sum_{l=2..n} (n - l + 1)*(l - 1)*num_binarias
    #   = num_binarias * (n^3 - n) / 6
    if n <= 0:
        return 1
    evaluaciones_fase1 = n * num_terminales
    evaluaciones_fase2 = num_binarias * (n ** 3 - n) // 6
    # cada evaluacion en Fase 1 realiza 2 operaciones elementales (comparar terminal y actualizar celda)
    # cada evaluacion en Fase 2 realiza 4 operaciones elementales (verificar B en T[i][k], C en T[k+1][j], etc.)
    # mas el control de ciclos: 2 + 2*n + 2*(n - 1) + 2*n*(n - 1)//2 + 2*(n^3 - n)//6
    ops_ciclos = 2 + 2 * n + 2 * (n - 1) + n * (n - 1) + (n ** 3 - n) // 3
    return ops_ciclos + 2 * evaluaciones_fase1 + 4 * evaluaciones_fase2


def algoritmo_cyk(gramatica, frase):
    # implementa el algoritmo CYK (Cocke-Younger-Kasami) mediante programacion dinamica
    palabras = tokenizar_frase(frase)
    n = len(palabras)
    operaciones = 2  # inicializacion y tokenizacion

    if n == 0:
        return {
            'frase': frase,
            'palabras': palabras,
            'n': 0,
            'aceptada': False,
            'tabla': [],
            'backpointers': [],
            'pasos_tabla': [],
            'derivacion': [],
            'arbol': [],
            'operaciones': 1,
            'evaluaciones_reglas': 0
        }

    # inicializar matriz triangular n x n de conjuntos y de backpointers
    tabla = [[set() for _ in range(n)] for _ in range(n)]
    backpointers = [[{} for _ in range(n)] for _ in range(n)]
    pasos_tabla = []
    evaluaciones_reglas = 0

    # Fase 1: subcadenas de longitud l = 1 (diagonal principal)
    for i in range(n):
        operaciones += 2  # avance de ciclo i y lectura de palabra
        palabra = palabras[i]
        reglas_celda = []

        for variable, terminal in gramatica.producciones_terminales:
            evaluaciones_reglas += 1
            operaciones += 2  # comparacion de produccion terminal A -> a
            if terminal == palabra:
                tabla[i][i].add(variable)
                if variable not in backpointers[i][i]:
                    backpointers[i][i][variable] = []
                backpointers[i][i][variable].append(('terminal', palabra))
                reglas_celda.append(f"{variable} -> '{palabra}'")

        pasos_tabla.append({
            'longitud': 1,
            'i': i + 1,
            'j': i + 1,
            'subcadena': palabra,
            'variables': sorted(tabla[i][i]),
            'detalle': reglas_celda
        })

    # Fase 2: subcadenas de longitud l = 2 hasta n
    for l in range(2, n + 1):
        operaciones += 2  # control de ciclo externo l
        for i in range(0, n - l + 1):
            j = i + l - 1
            operaciones += 2  # control de ciclo medio i y calculo de j
            reglas_celda = []

            for k in range(i, j):
                operaciones += 2  # control de ciclo de particion k
                izquierda_set = tabla[i][k]
                derecha_set = tabla[k + 1][j]

                for a, b, c in gramatica.producciones_binarias:
                    evaluaciones_reglas += 1
                    operaciones += 4  # verificacion de pertenencia B in T[i,k] y C in T[k+1,j]
                    if b in izquierda_set and c in derecha_set:
                        tabla[i][j].add(a)
                        if a not in backpointers[i][j]:
                            backpointers[i][j][a] = []
                        backpointers[i][j][a].append(('binaria', k, b, c))
                        reglas_celda.append(
                            f"{a} -> {b} [{i+1},{k+1}] + {c} [{k+2},{j+1}]"
                        )

            pasos_tabla.append({
                'longitud': l,
                'i': i + 1,
                'j': j + 1,
                'subcadena': " ".join(palabras[i:j + 1]),
                'variables': sorted(tabla[i][j]),
                'detalle': reglas_celda
            })

    aceptada = gramatica.simbolo_inicial in tabla[0][n - 1]
    derivacion = []
    arbol = []

    if aceptada:
        derivacion = generar_derivacion_izquierda_cyk(
            backpointers, n, gramatica.simbolo_inicial
        )
        arbol = construir_arbol_ascii(
            backpointers, 0, n - 1, gramatica.simbolo_inicial
        )

    return {
        'frase': frase,
        'palabras': palabras,
        'n': n,
        'aceptada': aceptada,
        'tabla': tabla,
        'backpointers': backpointers,
        'pasos_tabla': pasos_tabla,
        'derivacion': derivacion,
        'arbol': arbol,
        'operaciones': operaciones,
        'evaluaciones_reglas': evaluaciones_reglas
    }


def formatear_matriz_cyk(palabras, tabla):
    # construye una vista tabular limpia de la matriz triangular CYK
    n = len(palabras)
    if n == 0:
        return "  (Tabla vacia)"

    ancho_col = max(12, max(len(w) + 4 for w in palabras))
    lineas = []

    # encabezado con los indices j y las palabras
    encabezado_j = "      |" + "|".join(f" j={j+1}: {palabras[j]:<{ancho_col-6}} " for j in range(n)) + "|"
    separador = "------+" + "+".join("-" * (ancho_col + 1) for _ in range(n)) + "+"
    lineas.append(separador)
    lineas.append(encabezado_j)
    lineas.append(separador)

    for i in range(n):
        celdas = []
        for j in range(n):
            if j < i:
                contenido = "-"
            else:
                vars_celda = sorted(tabla[i][j])
                contenido = "{" + ",".join(vars_celda) + "}" if vars_celda else "{}"
            celdas.append(f" {contenido:^{ancho_col}}")
        lineas.append(f" i={i+1:<2} |" + "|".join(celdas) + "|")
    lineas.append(separador)
    return "\n".join(lineas)


def formatear_resultado_cyk(resultado):
    # genera un reporte completo del reconocimiento con el algoritmo CYK
    lineas = []
    lineas.append("=" * 78)
    lineas.append(f"RECONOCIMIENTO CON ALGORITMO CYK - Frase: \"{resultado['frase']}\"")
    lineas.append("=" * 78)
    lineas.append(f"Tokens (n = {resultado['n']}): {resultado['palabras']}")
    estado_str = "ACEPTADA" if resultado['aceptada'] else "RECHAZADA"
    lineas.append(f"Resultado: {estado_str} ('S' {'SI' if resultado['aceptada'] else 'NO'} esta en T[1, {resultado['n']}])")
    lineas.append(f"Evaluaciones de producciones: {resultado['evaluaciones_reglas']}")
    lineas.append(f"Conteo total de operaciones (CYK): {resultado['operaciones']}")

    lineas.append("\n1. Matriz Triangular CYK T[i, j]:")
    lineas.append(formatear_matriz_cyk(resultado['palabras'], resultado['tabla']))

    lineas.append("\n2. Registro Paso a Paso del Llenado de Celdas (solo celdas no vacias o nivel 1):")
    longitud_actual = 0
    for paso in resultado['pasos_tabla']:
        if paso['longitud'] != longitud_actual:
            longitud_actual = paso['longitud']
            lineas.append(f"  -- Nivel l = {longitud_actual} (subcadenas de longitud {longitud_actual}) --")
        if paso['longitud'] == 1 or paso['variables']:
            vars_str = "{" + ", ".join(paso['variables']) + "}" if paso['variables'] else "{}"
            det_str = "; ".join(paso['detalle']) if paso['detalle'] else "sin produccion"
            lineas.append(
                f"    T[{paso['i']},{paso['j']}] (\"{paso['subcadena']}\") = {vars_str:<12} <= {det_str}"
            )

    if resultado['aceptada']:
        lineas.append("\n3. Pasos de Derivacion Reconstruidos (desde S):")
        for idx, paso in enumerate(resultado['derivacion']):
            prefijo = "   " if idx == 0 else " => "
            lineas.append(f"  {prefijo}{paso}")

        lineas.append("\n4. Arbol de Parseo Sintactico:")
        for linea_arbol in resultado['arbol']:
            lineas.append(f"  {linea_arbol}")

    return "\n".join(lineas)


# pda.py
from models import Estado, PDA, Pila, DescripcionInstantanea
from gramatica import tokenizar_frase


def gramatica_a_pda(gramatica):
    # convierte una gramatica libre de contexto G = (V, Sigma, S, P) a un PDA equivalente

    q0 = Estado(es_aceptacion=False, nombre="q0")
    q1 = Estado(es_aceptacion=False, nombre="q1")
    q2 = Estado(es_aceptacion=True, nombre="q2")

    pda = PDA(estado_inicial=q0, simbolo_inicial_pila='Z0')
    pda.estados = [q0, q1, q2]
    pda.estados_aceptacion = [q2]
    pda.alfabeto_entrada = set(gramatica.terminales)
    pda.alfabeto_pila = set(gramatica.variables) | set(gramatica.terminales) | {'Z0'}

    # 1. transicion inicial: empujar el simbolo inicial S sobre Z0 y pasar a q1
    q0.agregar_transicion_pda(
        simbolo_entrada='e',
        simbolo_pop='Z0',
        destino=q1,
        simbolos_push=[gramatica.simbolo_inicial, 'Z0'],
        etiqueta=f"Inicio: empujar {gramatica.simbolo_inicial} sobre Z0"
    )

    # 2. transiciones de expansion para cada produccion A -> alpha en P
    orden_vars = ['S', 'VP', 'PP', 'NP', 'V', 'P', 'N', 'Det']
    for variable in orden_vars:
        if variable in gramatica.producciones:
            for cuerpo in gramatica.producciones[variable]:
                cuerpo_str = " ".join(cuerpo)
                q1.agregar_transicion_pda(
                    simbolo_entrada='e',
                    simbolo_pop=variable,
                    destino=q1,
                    simbolos_push=list(cuerpo),
                    etiqueta=f"Produccion: {variable} -> {cuerpo_str}"
                )

    # 3. transiciones de emparejamiento para cada terminal a en Sigma
    for terminal in sorted(gramatica.terminales):
        q1.agregar_transicion_pda(
            simbolo_entrada=terminal,
            simbolo_pop=terminal,
            destino=q1,
            simbolos_push=[],
            etiqueta=f"Emparejar terminal: '{terminal}'"
        )

    # 4. transicion de aceptacion al detectar el fondo de la pila Z0
    q1.agregar_transicion_pda(
        simbolo_entrada='e',
        simbolo_pop='Z0',
        destino=q2,
        simbolos_push=[],
        etiqueta="Aceptacion: vaciar Z0 y pasar a q2"
    )

    return pda


def mostrar_definicion_pda(pda):
    # genera la representacion formal de la tupla M = (Q, Sigma, Gamma, delta, q0, Z0, F)
    lineas = []
    nombres_q = [e.nombre for e in pda.estados]
    nombres_f = [e.nombre for e in pda.estados_aceptacion]
    lineas.append("Definicion Formal del PDA: M = (Q, Sigma, Gamma, delta, q0, Z0, F)")
    lineas.append(f"  Q (Estados)           = {{{', '.join(nombres_q)}}}")
    lineas.append(f"  Sigma (Alf. Entrada)  = {{{', '.join(sorted(pda.alfabeto_entrada))}}}")
    lineas.append(f"  Gamma (Alf. Pila)     = {{{', '.join(sorted(pda.alfabeto_pila))}}}")
    lineas.append(f"  Estado Inicial        = {pda.estado_inicial.nombre}")
    lineas.append(f"  Simbolo Inicial Pila  = {pda.simbolo_inicial_pila}")
    lineas.append(f"  F (Aceptacion)        = {{{', '.join(nombres_f)}}}")
    lineas.append(f"  delta (Transiciones)  = ({sum(len(e.transiciones) for e in pda.estados)} transiciones en total):")

    for estado in pda.estados:
        for idx, t in enumerate(estado.transiciones, 1):
            push_str = " ".join(t.simbolos_push) if t.simbolos_push else "e"
            lineas.append(
                f"    delta({estado.nombre}, {t.simbolo}, {t.simbolo_pop}) -> "
                f"({t.destino.nombre}, {push_str:<6})   [{t.etiqueta}]"
            )
    return "\n".join(lineas)


def reconstruir_derivacion_izquierda(reglas_aplicadas, simbolo_inicial='S'):
    # reconstruye los pasos de derivacion por la izquierda a partir de las producciones usadas
    forma_sentencial = [simbolo_inicial]
    pasos = [" ".join(forma_sentencial)]

    for regla in reglas_aplicadas:
        if not regla.startswith("Produccion: "):
            continue
        texto_prod = regla.replace("Produccion: ", "")
        izquierda, derecha = texto_prod.split(" -> ")
        simbolos_der = derecha.split()

        # reemplaza la primera aparicion (mas a la izquierda) de la variable
        for i, sim in enumerate(forma_sentencial):
            if sim == izquierda:
                forma_sentencial = forma_sentencial[:i] + simbolos_der + forma_sentencial[i + 1:]
                pasos.append(f"{' '.join(forma_sentencial)}   (usando {izquierda} -> {derecha})")
                break

    return pasos


def simular_pda(pda, frase):
    # simula el reconocimiento de una frase empleando el PDA no determinista (con backtracking)
    palabras = tokenizar_frase(frase)
    n = len(palabras)
    operaciones = 1  # operacion inicial de tokenizacion y preparacion

    pila_inicial = Pila([pda.simbolo_inicial_pila])
    id_inicial = DescripcionInstantanea(
        estado=pda.estado_inicial.nombre,
        entrada_restante=palabras,
        pila_str=pila_inicial.como_cadena(),
        accion="Configuracion inicial"
    )
    operaciones += 2

    if n == 0:
        return {
            'frase': frase,
            'palabras': palabras,
            'n': 0,
            'aceptada': False,
            'descripciones_instantaneas': [id_inicial],
            'derivacion': [],
            'operaciones': operaciones,
            'configuraciones_exploradas': 1,
            'motivo_rechazo': "La cadena vacia no pertenece a la gramatica CNF."
        }

    # verificacion de palabras fuera del alfabeto para reportar diagnostico claro
    palabras_invalidas = [w for w in palabras if w not in pda.alfabeto_entrada]

    # pila de busqueda DFS para manejar el no determinismo del PDA
    # cada entrada contiene: (estado_actual, indice_palabra, pila_actual, historial_ids, reglas_aplicadas)
    frontera = [(pda.estado_inicial, 0, pila_inicial, [id_inicial], [])]
    operaciones += 1

    configuraciones_exploradas = 0
    mejor_intento_ids = [id_inicial]

    while frontera:
        estado_act, idx, pila_act, hist_ids, reglas = frontera.pop()
        configuraciones_exploradas += 1
        operaciones += 2  # extraccion de frontera y conteo de estado

        if len(hist_ids) > len(mejor_intento_ids):
            mejor_intento_ids = hist_ids

        # verificar condicion de aceptacion: estado final, entrada consumida y pila vacia
        operaciones += 3
        if estado_act.es_aceptacion and idx == n and pila_act.esta_vacia():
            derivacion = reconstruir_derivacion_izquierda(reglas)
            return {
                'frase': frase,
                'palabras': palabras,
                'n': n,
                'aceptada': True,
                'descripciones_instantaneas': hist_ids,
                'derivacion': derivacion,
                'operaciones': operaciones,
                'configuraciones_exploradas': configuraciones_exploradas,
                'motivo_rechazo': None
            }

        tope_actual = pila_act.tope()
        operaciones += 1
        if tope_actual is None:
            continue

        # recolectar transiciones aplicables desde el estado actual
        hijos = []
        for trans in estado_act.transiciones:
            operaciones += 1  # comparacion de simbolo de pila
            if trans.simbolo_pop != tope_actual:
                continue

            # caso 1: transicion epsilon (sin consumir palabra de entrada)
            if trans.simbolo == 'e':
                operaciones += 1
                # la transicion de vaciar Z0 solo conduce a aceptacion si ya se consumio toda la entrada
                if tope_actual == pda.simbolo_inicial_pila and trans.destino.es_aceptacion and idx < n:
                    operaciones += 1
                    continue

                # calcular cuantos simbolos gramaticales (sin contar Z0) quedarian en la pila
                # como la gramatica esta en CNF sin producciones epsilon, cada simbolo en la pila
                # requiere al menos 1 palabra restante en la entrada
                simbolos_gram_actuales = len(pila_act) - (1 if pda.simbolo_inicial_pila in pila_act.elementos else 0)
                nuevos_simbolos_gram = len([s for s in trans.simbolos_push if s != pda.simbolo_inicial_pila])
                simbolos_gram_resultantes = simbolos_gram_actuales - 1 + nuevos_simbolos_gram
                palabras_restantes = n - idx
                operaciones += 4

                if simbolos_gram_resultantes > palabras_restantes:
                    # poda por longitud: la rama generaria una cadena de longitud mayor a n
                    continue

                nueva_pila = pila_act.clonar()
                nueva_pila.pop()
                nueva_pila.push_secuencia(trans.simbolos_push)
                operaciones += 2 + len(trans.simbolos_push)

                nueva_id = DescripcionInstantanea(
                    estado=trans.destino.nombre,
                    entrada_restante=palabras[idx:],
                    pila_str=nueva_pila.como_cadena(),
                    accion=trans.etiqueta
                )
                hijos.append((
                    trans.destino,
                    idx,
                    nueva_pila,
                    hist_ids + [nueva_id],
                    reglas + [trans.etiqueta]
                ))

            # caso 2: transicion que consume un terminal de la entrada
            else:
                operaciones += 2  # verificar limites de entrada y coincidencia del token
                if idx < n and palabras[idx] == trans.simbolo:
                    nueva_pila = pila_act.clonar()
                    nueva_pila.pop()
                    nueva_pila.push_secuencia(trans.simbolos_push)
                    operaciones += 2 + len(trans.simbolos_push)

                    nueva_id = DescripcionInstantanea(
                        estado=trans.destino.nombre,
                        entrada_restante=palabras[idx + 1:],
                        pila_str=nueva_pila.como_cadena(),
                        accion=trans.etiqueta
                    )
                    hijos.append((
                        trans.destino,
                        idx + 1,
                        nueva_pila,
                        hist_ids + [nueva_id],
                        reglas + [trans.etiqueta]
                    ))

        # se agregan en orden inverso para que DFS explore primero las producciones en el orden definido
        for hijo in reversed(hijos):
            frontera.append(hijo)
            operaciones += 1

    motivo = "No existe derivacion valida en la gramatica G para esta estructura sintactica."
    if palabras_invalidas:
        motivo = f"Palabras fuera del alfabeto Sigma: {palabras_invalidas}"

    return {
        'frase': frase,
        'palabras': palabras,
        'n': n,
        'aceptada': False,
        'descripciones_instantaneas': mejor_intento_ids,
        'derivacion': [],
        'operaciones': operaciones,
        'configuraciones_exploradas': configuraciones_exploradas,
        'motivo_rechazo': motivo
    }


def formatear_resultado_pda(resultado):
    # genera un reporte detallado de los pasos del PDA (descripciones instantaneas y derivacion)
    lineas = []
    lineas.append("=" * 78)
    lineas.append(f"RECONOCIMIENTO CON PDA - Frase: \"{resultado['frase']}\"")
    lineas.append("=" * 78)
    lineas.append(f"Tokens (n = {resultado['n']}): {resultado['palabras']}")
    estado_str = "ACEPTADA" if resultado['aceptada'] else "RECHAZADA"
    lineas.append(f"Resultado: {estado_str}")
    lineas.append(f"Configuraciones exploradas: {resultado['configuraciones_exploradas']}")
    lineas.append(f"Conteo total de operaciones (PDA): {resultado['operaciones']}")

    if resultado['aceptada']:
        lineas.append("\n1. Registro de Descripciones Instantaneas (q, w, gamma):")
        for i, desc in enumerate(resultado['descripciones_instantaneas']):
            prefijo = "   " if i == 0 else " |- "
            lineas.append(f"  Paso {i:>2}:{prefijo}{desc.formatear()}")

        lineas.append("\n2. Pasos de Derivacion por la Izquierda:")
        for i, paso in enumerate(resultado['derivacion']):
            prefijo = "   " if i == 0 else " => "
            lineas.append(f"  {prefijo}{paso}")
    else:
        lineas.append(f"\nMotivo de rechazo: {resultado['motivo_rechazo']}")
        lineas.append("\nRama mas profunda alcanzada (Descripciones Instantaneas):")
        for i, desc in enumerate(resultado['descripciones_instantaneas']):
            prefijo = "   " if i == 0 else " |- "
            lineas.append(f"  Paso {i:>2}:{prefijo}{desc.formatear()}")

    return "\n".join(lineas)


# gramatica.py

class GramaticaLibreContexto:
    def __init__(self, simbolo_inicial='S'):
        self.variables = set()
        self.terminales = set()
        self.simbolo_inicial = simbolo_inicial
        # diccionario: variable -> lista de tuplas con el lado derecho de la produccion
        self.producciones = {}
        # listas separadas para facilitar el algoritmo CYK (Forma Normal de Chomsky)
        self.producciones_binarias = []   # tuplas (A, B, C) para A -> B C
        self.producciones_terminales = [] # tuplas (A, a) para A -> a

    def agregar_produccion(self, variable, cuerpo):
        # cuerpo es una lista o tupla de simbolos, ej. ['NP', 'VP'] o ['cooks']
        cuerpo_tupla = tuple(cuerpo)
        self.variables.add(variable)
        if variable not in self.producciones:
            self.producciones[variable] = []
        if cuerpo_tupla not in self.producciones[variable]:
            self.producciones[variable].append(cuerpo_tupla)

        if len(cuerpo_tupla) == 2:
            b, c = cuerpo_tupla
            self.variables.add(b)
            self.variables.add(c)
            self.producciones_binarias.append((variable, b, c))
        elif len(cuerpo_tupla) == 1:
            a = cuerpo_tupla[0]
            self.terminales.add(a)
            self.producciones_terminales.append((variable, a))

    def mostrar_gramatica(self):
        lineas = []
        lineas.append("Gramatica G = (V, Sigma, S, P)")
        lineas.append(f"  V (Variables)  = {{{', '.join(sorted(self.variables))}}}")
        lineas.append(f"  Sigma (Terms)  = {{{', '.join(sorted(self.terminales))}}}")
        lineas.append(f"  S (Inicial)    = {self.simbolo_inicial}")
        lineas.append("  P (Producciones):")
        orden_vars = ['S', 'VP', 'PP', 'NP', 'V', 'P', 'N', 'Det']
        for v in orden_vars:
            if v in self.producciones:
                cuerpos = [" ".join(c) for c in self.producciones[v]]
                lineas.append(f"    {v:<4} -> {' | '.join(cuerpos)}")
        return "\n".join(lineas)


def construir_gramatica_proyecto2():
    # construye la gramatica G en Forma Normal de Chomsky especificada en el Proyecto #2
    g = GramaticaLibreContexto(simbolo_inicial='S')

    # S -> NP VP
    g.agregar_produccion('S', ['NP', 'VP'])

    # VP -> VP PP | V NP | cooks | drinks | eats | cuts
    g.agregar_produccion('VP', ['VP', 'PP'])
    g.agregar_produccion('VP', ['V', 'NP'])
    for verbo in ['cooks', 'drinks', 'eats', 'cuts']:
        g.agregar_produccion('VP', [verbo])

    # PP -> P NP
    g.agregar_produccion('PP', ['P', 'NP'])

    # NP -> Det N | he | she
    g.agregar_produccion('NP', ['Det', 'N'])
    for pronombre in ['he', 'she']:
        g.agregar_produccion('NP', [pronombre])

    # V -> cooks | drinks | eats | cuts
    for verbo in ['cooks', 'drinks', 'eats', 'cuts']:
        g.agregar_produccion('V', [verbo])

    # P -> in | with
    for prep in ['in', 'with']:
        g.agregar_produccion('P', [prep])

    # N -> cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
    sustantivos = [
        'cat', 'dog',
        'beer', 'cake', 'juice', 'meat', 'soup',
        'fork', 'knife', 'oven', 'spoon'
    ]
    for sust in sustantivos:
        g.agregar_produccion('N', [sust])

    # Det -> a | the
    for det in ['a', 'the']:
        g.agregar_produccion('Det', [det])

    return g


def tokenizar_frase(frase):
    # convierte una oracion en lista de palabras en minuscula ignorando puntuacion basica
    limpia = frase.strip().lower()
    for signo in ['.', ',', ';', '!', '?']:
        limpia = limpia.replace(signo, ' ')
    return [palabra for palabra in limpia.split() if palabra]


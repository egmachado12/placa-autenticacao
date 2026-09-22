"""Valida se um texto lido pelo OCR tem cara de placa brasileira.

Formatos:
- Antigo:   AAA0000   (3 letras + 4 números)
- Mercosul: AAA0A00   (3 letras + 1 número + 1 letra + 2 números)

O OCR erra com frequência em caracteres visualmente parecidos (0/O, 1/I,
8/B, 5/S, 2/Z). Em vez de só validar, tenta corrigir posição por posição
antes de rejeitar o texto.
"""

import re

PADRAO_ANTIGO = re.compile(r"^[A-Z]{3}\d{4}$")
PADRAO_MERCOSUL = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")

# Mapas de correção por "sentido" (quando a posição espera letra mas o OCR
# leu número, ou vice-versa).
NUMERO_PARA_LETRA = {"0": "O", "1": "I", "8": "B", "5": "S", "2": "Z"}
LETRA_PARA_NUMERO = {"O": "0", "I": "1", "B": "8", "S": "5", "Z": "2"}

# Posições 0,1,2 são sempre letra nos dois formatos.
# Mercosul: posição 4 também é letra (é o que diferencia do formato antigo).
POSICOES_LETRA_ANTIGO = {0, 1, 2}
POSICOES_LETRA_MERCOSUL = {0, 1, 2, 4}


def _corrigir(texto, posicoes_letra):
    """Ajusta cada caractere para letra ou número conforme a posição esperada."""
    corrigido = []
    for i, char in enumerate(texto):
        espera_letra = i in posicoes_letra
        if espera_letra and char in NUMERO_PARA_LETRA:
            corrigido.append(NUMERO_PARA_LETRA[char])
        elif not espera_letra and char in LETRA_PARA_NUMERO:
            corrigido.append(LETRA_PARA_NUMERO[char])
        else:
            corrigido.append(char)
    return "".join(corrigido)


def validar_placa(texto):
    """Tenta validar/corrigir o texto como placa BR (antiga ou Mercosul).

    Retorna a placa normalizada (str) se for válida, ou None caso não dê
    pra reconhecer nenhum dos dois formatos mesmo após a correção.
    """
    if not texto or len(texto) != 7:
        return None

    texto = texto.upper()

    candidato_antigo = _corrigir(texto, POSICOES_LETRA_ANTIGO)
    if PADRAO_ANTIGO.match(candidato_antigo):
        return candidato_antigo

    candidato_mercosul = _corrigir(texto, POSICOES_LETRA_MERCOSUL)
    if PADRAO_MERCOSUL.match(candidato_mercosul):
        return candidato_mercosul

    return None

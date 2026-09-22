"""Extrai o texto de um recorte candidato a placa usando EasyOCR."""

import cv2
import easyocr

# O reader carrega os pesos do modelo de OCR na memória — é caro (alguns
# segundos). Por isso é criado uma única vez no nível do módulo, não a
# cada chamada de `ler_placa`.
_leitor = easyocr.Reader(["en"], gpu=False)


def preprocessar(recorte):
    """Prepara o recorte para o OCR: cinza + contraste + binarização."""
    cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    cinza = cv2.equalizeHist(cinza)
    _, binaria = cv2.threshold(
        cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return binaria


def ler_placa(recorte):
    """Roda o OCR no recorte e devolve o texto bruto mais provável.

    Retorna None se o OCR não conseguiu extrair nenhum texto com confiança
    mínima aceitável.
    """
    imagem_preparada = preprocessar(recorte)
    resultados = _leitor.readtext(imagem_preparada)

    if not resultados:
        return None

    # readtext devolve [(caixa, texto, confianca), ...]; fica com o de
    # maior confiança, que tende a ser o texto principal do recorte.
    _, texto, confianca = max(resultados, key=lambda r: r[2])

    if confianca < 0.3:
        return None

    return texto.upper().replace(" ", "")

"""Localiza, no frame, a região onde provavelmente está a placa.

Abordagem OpenCV clássica (sem rede neural): a placa costuma aparecer como
um retângulo bem definido, com bastante contraste e uma proporção
largura/altura característica. A estratégia é: reduzir ruído -> realçar
bordas -> achar contornos -> filtrar os que "parecem placa".
"""

import cv2

# Proporção largura/altura de uma placa BR (~ 40cm x 13cm) com folga.
PROPORCAO_MIN = 2.0
PROPORCAO_MAX = 6.0
AREA_MINIMA = 800  # descarta contornos pequenos demais (ruído)

# Quantos candidatos, no máximo, seguem para o OCR (etapa cara, uma rede
# neural rodando em CPU). Canny+findContours pode gerar dezenas/centenas
# de retângulos "parecidos com placa" por frame; sem esse limite, o OCR
# roda em cada um deles e o pipeline trava.
MAX_CANDIDATOS = 5


def detectar_placas(frame):
    """Retorna os candidatos mais prováveis de serem a placa no frame.

    No máximo MAX_CANDIDATOS itens, ordenados do maior para o menor (placa
    de verdade tende a ser um dos maiores retângulos válidos do quadro).
    Cada item é uma tupla (recorte, bbox): o recorte é a imagem BGR pronta
    para o OCR, e bbox=(x, y, largura, altura) é a posição no frame
    original, usada para desenhar o retângulo na tela.
    """
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    suavizado = cv2.bilateralFilter(cinza, 11, 17, 17)
    bordas = cv2.Canny(suavizado, 30, 200)

    contornos, _ = cv2.findContours(
        bordas, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    candidatos = []
    for contorno in contornos:
        x, y, largura, altura = cv2.boundingRect(contorno)
        if altura == 0:
            continue

        area = largura * altura
        proporcao = largura / altura

        if area < AREA_MINIMA:
            continue
        if not (PROPORCAO_MIN <= proporcao <= PROPORCAO_MAX):
            continue

        recorte = frame[y : y + altura, x : x + largura]
        candidatos.append((area, recorte, (x, y, largura, altura)))

    candidatos.sort(key=lambda item: item[0], reverse=True)
    maiores = candidatos[:MAX_CANDIDATOS]

    return [(recorte, bbox) for _, recorte, bbox in maiores]


if __name__ == "__main__":
    from captura import gerar_frames

    for frame in gerar_frames(0):
        candidatos = detectar_placas(frame)
        for i, (recorte, _) in enumerate(candidatos):
            cv2.imshow(f"candidato {i}", recorte)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

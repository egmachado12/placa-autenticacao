"""Núcleo do pipeline, sem autenticação/banco ainda.

captura -> detecção -> OCR -> validação

Objetivo desta etapa: provar que a cadeia inteira funciona de ponta a
ponta antes de integrar a lista branca e os logs.
"""

import sys

import cv2

from captura import gerar_frames
from deteccao_placa import detectar_placas
from ocr import ler_placa
from validacao import validar_placa


def processar_frame(frame):
    """Roda detecção -> OCR -> validação num único frame.

    Retorna uma lista de (placa, bbox) para cada leitura válida (pode ser
    vazia, e normalmente será, já que a maioria dos candidatos de
    deteccao_placa.py não é uma placa de verdade).
    """
    deteccoes = []

    for recorte, bbox in detectar_placas(frame):
        texto_bruto = ler_placa(recorte)
        if texto_bruto is None:
            continue

        placa = validar_placa(texto_bruto)
        if placa is not None:
            deteccoes.append((placa, bbox))

    return deteccoes


def desenhar_deteccoes(frame, deteccoes):
    """Desenha um retângulo verde + o texto da placa sobre o frame."""
    for placa, (x, y, largura, altura) in deteccoes:
        cv2.rectangle(frame, (x, y), (x + largura, y + altura), (0, 255, 0), 2)
        cv2.putText(
            frame,
            placa,
            (x, y - 10 if y > 20 else y + altura + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )


# Processa 1 a cada N frames. Um vídeo tem ~30 frames/segundo, mas o
# carro não anda tão rápido assim: não precisamos rodar o pipeline caro
# (detecção + OCR) em todo frame para não perder nenhuma placa.
PULAR_FRAMES = 5


def main(fonte=0):
    print(f"Iniciando pipeline. Fonte: {fonte}. Pressione 'q' para sair.")

    # Guarda a última detecção válida para continuar desenhando o
    # retângulo nos frames "pulados", já que só reprocessamos 1 a cada
    # PULAR_FRAMES — sem isso, o retângulo apareceria só 1 frame e sumiria.
    ultimas_deteccoes = []

    for indice, frame in enumerate(gerar_frames(fonte)):
        if indice % PULAR_FRAMES == 0:
            deteccoes = processar_frame(frame)
            if deteccoes:
                ultimas_deteccoes = deteccoes
                for placa, _ in deteccoes:
                    print(f"Placa reconhecida: {placa}")

        desenhar_deteccoes(frame, ultimas_deteccoes)
        cv2.imshow("placa-autenticacao (núcleo)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Uso: python main.py            -> webcam
    #      python main.py video.mp4  -> arquivo de vídeo
    fonte_video = sys.argv[1] if len(sys.argv) > 1 else 0
    main(fonte_video)

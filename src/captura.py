"""Fonte de frames do pipeline: webcam ao vivo ou arquivo de vídeo gravado."""

import cv2


def gerar_frames(fonte=0):
    """Abre a fonte de vídeo e entrega um frame por vez.

    fonte=0 (ou outro índice int) -> webcam.
    fonte="caminho/video.mp4" -> arquivo de vídeo gravado.

    É um gerador: cada chamada de `next()` (ou cada volta do `for`) devolve
    o próximo frame, sem carregar o vídeo inteiro na memória de uma vez.
    """
    captura = cv2.VideoCapture(fonte)

    if not captura.isOpened():
        raise RuntimeError(f"Não foi possível abrir a fonte de vídeo: {fonte}")

    try:
        while True:
            lido, frame = captura.read()
            if not lido:
                break
            yield frame
    finally:
        captura.release()


if __name__ == "__main__":
    total = 0
    for frame in gerar_frames(0):
        total += 1
        cv2.imshow("captura - pressione 'q' para sair", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
    print(f"Frames capturados: {total}")

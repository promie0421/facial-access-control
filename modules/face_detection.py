def contar_rostos(rostos):
    return len(rostos)


def obter_bounding_boxes(rostos):
    """Retorna as posições dos rostos detectados."""
    boxes = []

    for rosto in rostos:
        x1, y1, x2, y2 = rosto.bbox.astype(int)
        boxes.append((x1, y1, x2, y2))

    return boxes
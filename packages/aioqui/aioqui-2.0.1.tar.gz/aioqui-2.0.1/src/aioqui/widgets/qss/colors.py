LAYER_1 = '#0E1621'
LAYER_2 = '#17212B'
LAYER_3 = '#242F3D'
LAYER_4 = '#023535'
LAYER_5 = '#008F8C'
LAYER_6 = '#3E546A'

TRANSPARENT = 'transparent'

RED = 'rgba(182, 0, 40, 1)'
GREEN = 'darkgreen'

RED_HOVER = 'rgba(182, 0, 40, 0.5)'
GREEN_HOVER = 'rgba(0, 255, 0, 0.5)'
HOVER = 'rgba(255, 255, 255, 0.1)'

TEXT_PRIMARY = 'white'
TEXT_SECONDARY = 'gray'
TEXT_ALERT = 'red'


def gradient(
        p1: tuple[int, int] = (0, 0), p2: tuple[int, int] = (0, 1),
        c1: str = '#cccccc', c2: str = '#333333'
) -> str:
    return f'qlineargradient(x1: {p1[0]}, y1: {p1[1]}, x2: {p2[0]}, y2: {p2[1]}, stop: 0 {c1}, stop: 1 {c2})'

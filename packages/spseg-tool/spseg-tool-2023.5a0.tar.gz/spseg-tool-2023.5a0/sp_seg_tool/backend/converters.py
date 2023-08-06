import numpy as np


def rgb2hsl(rgb):
    nr, ng, nb = rgb / np.max(rgb, axis=0)
    cmax = np.max([nr, ng, nb])
    cmin = np.min([nr, ng, nb])
    delta = cmax - cmin
    luminance = (cmax + cmin) / 2
    if np.abs(delta) < 1e-7:
        saturation = 0
        hue = 0
    else:
        saturation = delta / (1 - np.abs(2 * luminance - 1))

    color_idx = np.argmax([nr, ng, nb])
    if color_idx == 0:
        hue = 60 * ((ng - nb) / delta) % 6
    elif color_idx == 1:
        hue = 60 * ((nb - nr) / delta + 2)
    else:
        hue = 60 * ((nr, ng) / delta + 4)

    return np.stack((hue, saturation, luminance)).T


def rgb2ycbcr(rgb):
    weights = np.array(
        [
            [0.299, 0.587, 0.114],
            [-0.1687, -0.3313, 0.5],
            [0.5, -0.4187, -0.0813],
        ]
    )
    ycbcr = rgb @ weights.T
    ycbcr[:, :, [1, 2]] += 128
    return ycbcr / np.max(ycbcr)

def hex2rgb(h, relative=True):

    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    if relative:

        r = rgb[0] / 255.0
        g = rgb[1] / 255.0
        b = rgb[2] / 255.0

        rgb = (r,g,b)

    return rgb

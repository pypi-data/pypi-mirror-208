import matplotlib

from .make_cmap import make_cmap
from .hex2rgb import hex2rgb


# -------------------------------------------------------------------------------------------------
color_gridlines_major = '#666666'
color_gridlines_minor = '#999999'
# -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
black = '#000000'
white = '#ffffff'
# -------------------------------------------------------------------------------------------------


# flat_ui_palette_v1

peter_river = '#3498db'
wet_asphalt = '#34495e'
orange      = '#f39c12'
alizarin    = '#e74c3c'
emerald     = '#2ecc71'
sun_flower  = '#f1c40f'
pomegranate = '#c0392b'
wisteria    = '#8e44ad'
belize_hole = '#2980b9'
amethyst    = '#9b59b6'
turquoise   = '#1abc9c'
green_sea   = '#16a085'
nephritis   = '#27ae60'

midnight_blue = '#2c3e50'

clouds      = '#ecf0f1'
silver      = '#bdc3c7'
concrete    = '#95a5a6'
asbestos    = '#7f8c8d'

# aussie palette
pure_apple   = '#6ab04c'
carmine_pink = '#eb4d4b'
turbo        = '#f9ca24'
quince_jelly = '#f0932b'
pink_glamour = '#ff7979'
exodus_fruit = '#686de0'

# spanish palette
summer_sky      = '#34ace0'
fluorescent_red = '#ff5252'
celestial_green = '#33d9b2'

radical_red = '#ff355e'


black_rgb = hex2rgb(black.lstrip('#'))
white_rgb = hex2rgb(white.lstrip('#'))

clouds_rgb = hex2rgb(clouds.lstrip('#'))

wisteria_rgb = hex2rgb(wisteria.lstrip('#'))

peter_river_rgb = hex2rgb(peter_river.lstrip('#'))
belize_hole_rgb = hex2rgb(belize_hole.lstrip('#'))

sun_flower_rgb = hex2rgb(sun_flower.lstrip('#'))
radical_red_rgb = hex2rgb(radical_red.lstrip('#'))


orange_rgb = hex2rgb(orange.lstrip('#'))

# -------------------------------------------------------------------------------------------------
# colormap density

colors = [black_rgb, wisteria_rgb, belize_hole_rgb, peter_river_rgb, white_rgb]

positions = [0.0, 0.2, 0.5, 0.6, 1.0]

cmap_density = make_cmap(colors, positions=positions)
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
# colormap real part

colors_tmp = [radical_red_rgb, black_rgb, peter_river_rgb]
positions_tmp = [0.0, 0.5, 1.0]

cmap_real_part = make_cmap(colors_tmp, positions=positions_tmp)

color_1_tmp = cmap_real_part(0.25)
color_2_tmp = cmap_real_part(0.75)

colors_tmp = [radical_red_rgb, color_1_tmp, black_rgb, color_2_tmp, peter_river_rgb]
positions_tmp = [0.0, 0.4, 0.5, 0.6, 1.0]

cmap_real_part = make_cmap(colors_tmp, positions=positions_tmp)

# cmap_real = matplotlib.cm.PRGn

cmap_real_part = matplotlib.cm.RdBu
# -------------------------------------------------------------------------------------------------

# cmap = matplotlib.cm.PiYG
# cmap = matplotlib.cm.PRGn
# cmap = matplotlib.cm.RdGy
# cmap = matplotlib.cm.RdBu
# cmap = matplotlib.cm.RdYlBu
# cmap = matplotlib.cm.bwr
# cmap = matplotlib.cm.Spectral
# cmap = matplotlib.cm.coolwarm

# cmap_density = matplotlib.cm.hot
# cmap_density = matplotlib.cm.cool
# cmap_density = matplotlib.cm.Blues
# cmap_density = matplotlib.cm.binary
# cmap_density = matplotlib.cm.gist_yarg
# cmap_density = matplotlib.cm.Greys
# cmap_density = matplotlib.cm.GnBu
# cmap_density = matplotlib.cm.YlGn

# cmap_real_part = matplotlib.cm.RdBu
# cmap_real_part = matplotlib.cm.RdGy
# cmap_real_part = matplotlib.cm.Spectral
# cmap_real_part = matplotlib.cm.RdGy
# cmap_real_part = matplotlib.cm.PiYG
# cmap_real_part = matplotlib.cm.RdYlBu
# cmap_real_part = matplotlib.cm.PRGn
# cmap_real_part = matplotlib.cm.bwr

# cmap_density = matplotlib.colors.LinearSegmentedColormap.from_list(
#     'colormap_1',
#     [
#     black,
#     wisteria,
#     belize_hole,
#     peter_river,
#     clouds
#     ],
#     N=512)

# cmap_density = matplotlib.colors.LinearSegmentedColormap.from_list(
#     'colormap_1',
#     [
#     clouds,
#     peter_river,
#     belize_hole,
#     wisteria,
#     black
#     ],
#     N=512)

# cmap_real_part = matplotlib.colors.LinearSegmentedColormap.from_list(
#     'colormap_1',
#     [
#     peter_river,
#     black,
#     sun_flower
#     ],
#     N=512)

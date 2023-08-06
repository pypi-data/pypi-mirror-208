from noaawc.animate import Create_plot_gif as Cpf
from noawclg.main import get_noaa_data as gnd

def test_render():
    dn = gnd(date='26/01/2023')

    point_init=[-9.43,-89]
    point_jua = [-9.43,-40.50]

    gif = Cpf(dn=dn)
    cmap = 'inferno'
    gif.path_save=f'tests_gifs/{cmap}_test_spin_temp_wind.gif'
    gif.key_noaa = 'tmpmwl'
    gif.title='temperatura dos jatos de vento'
    gif.point_init=point_init
    gif.point_end=point_jua
    gif.lon_stop=-39
    gif.cmap = cmap

    gif.tracing()
    gif.render()
from noaawc.animate import Create_plot_gif as Cpf
from noawclg.main import get_noaa_data as gnd


def test_render():
    dn = gnd(date='26/01/2023')

    point_init=[-9.43,-89]
    point_jua = [-9.43,-40.50]

    gif = Cpf(dn=dn)
    gif.path_save='tests_gifs/surface_temp/CMRmap_test_spin_temp_surface.gif'
    gif.key_noaa = 'tmpsfc'
    gif.title='temperatura da superficie'
    gif.point_init=point_init
    gif.point_end=point_jua
    gif.lon_stop=-39
    gif.annotate_loc_txt = '. Nova York: %(data)sºC'
    gif.color_annote_loc = 'white'
    gif.cmap = 'CMRmap'
    #gif.annotate_focus_txt = '. Juazeiro: %(data)sºC'

    gif.tracing()
    gif.render()
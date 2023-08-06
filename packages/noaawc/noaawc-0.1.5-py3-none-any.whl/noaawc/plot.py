
import numpy as np
#import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from noawclg import get_noaa_data as gnd
import pandas as pd
from dataclasses import dataclass
import datetime
from kitano.logging import puts

# global dn
# global date_base

# date_base = None
# def set_date(date:str):
#     date_base = date
#     print('oi')

# def load_data():
#     if date_base:
#         puts(f'loading data from date {date_base}')
#         dn = gnd(date=date_base)
#     else:
#         today = datetime.datetime.now()
#         yesterday = today - datetime.timedelta(days=1)
#         yesterday = yesterday.strftime('%d/%m/%Y')
#         puts(f'loading data from yesterday date {yesterday}')
#         dn = gnd(date=yesterday)

#keys = dn.get_noaa_keys()
'''
the function base and more
important from it work
'''

plt.style.use('dark_background')

@dataclass
class plot_global:
    dn:gnd
    path:str='plot.png'
    indice:int=0
    date:str=None
    title:str='plot'
    text:str=False
    pos_text:tuple=False
    annotate:str=False
    pos_annotate:tuple=False
    text_color:str='white'
    text_size=9
    fontweight_text='bold'
    facecolor_text:str='red'
    edgecolor_text:str='black'
    annotate_size:float=9
    annotate_color:str='white'
    loc_focus:tuple=(0,0)
    key_noaa:str='tmpmwl'
    subtr_data:str=273,
    text_cb:str='ºC'
    alpha:float=.9
    author:str='@gpftc_ | @reinanbr_'
    level_data:int=25
    resolution:str='c'
    keys:str = ''
    fillcontinents_colors:str = ''
    cmap:plt.cm = plt.cm.inferno
    ax:plt.subplot = plt.subplot(111)
    plt:plt=plt
    
    line_states:float=0.1
    line_countries:float=0.35
    
    xleft:int=None
    xright:int=None
    yup:int=None
    ydown:int=None
    
    annotate_pos_focus:tuple=None
    annotate_text_focus:str = None
    annotate_color_focus:str = "black"
    annotate_fontweight_focus:str = None
    
    annotate_loc_focus:tuple=None
    annotate_loc_txt:str = None
    annotate_loc_color:str = 'black'
    fontweight_annote_loc:str = None
    #annotate_pos_focus:str = None
    
    
    
    
    def mining_data(self):
        
        self.fillcontinents_colors:str = {'color':'coral','lake_color':'aqua'}
        self.keys = self.dn.get_noaa_keys()
        self.data = self.dn[self.key_noaa][self.indice]-self.subtr_data
        self.data1 = self.dn[self.key_noaa][1]-self.subtr_data
        #import pandas as pd 
        self.lat  = self.dn['lat'][:]
        self.lon  = self.dn['lon'][:]
        self.data = self.dn[self.key_noaa][self.indice]-self.subtr_data
        self.data1 = self.dn[self.key_noaa][1]-self.subtr_data
        #print(len(data),len(lat))
        
        #if not self.indice==None:
        self.date_pd=self.dn['time'][self.indice].to_numpy()
        
        
        self.ts = pd.to_datetime(str(self.date_pd)) 
        self.date_text = self.ts.strftime('%d %h %Y\n %H:%M UTC')
        self.min_temp = self.data1.min()
        self.max_temp = self.data1.max()
        self.levels = np.linspace(self.min_temp,self.max_temp,self.level_data)

    def zoom(self,xright:int=None,xleft:int=None,ydown:int=None,yup:int=None):
        decai = 1000000
        if xleft and xright and yup and ydown:
            self.xright = xright*decai
            self.xleft = xleft*decai
            self.yup = yup*decai
            self.ydown = ydown*decai

    def rendering_image(self):
        self.m = Basemap(projection='ortho',
                         lat_0=self.loc_focus[0],
                         lon_0=self.loc_focus[1],
                         resolution=self.resolution,llcrnrx=self.xleft, llcrnry=self.ydown, urcrnrx=self.xright, urcrnry=self.yup, 
)
        #self.m.bluemarble(scale=.5)
        
        self.x, self.y = self.m(*np.meshgrid(self.lon,self.lat))
        
        self.m.fillcontinents(self.fillcontinents_colors['color'],
                             self.fillcontinents_colors['lake_color'])
        self.m.drawmapboundary(fill_color='aqua')
        self.cm=self.m.contourf(self.x,self.y,self.data,100,
                                alpha=self.alpha,
                                levels=self.levels,
                                cmap=self.cmap)
        #cm1=plt.contourf(x,y,data1,100,shading='nearest',cmap=plt.get_cmap('inferno'))
        #plt.cla()
        #plt.clf()
        self.cbar=self.plt.colorbar(self.cm,orientation='horizontal',extend='both',fraction=0.07,pad=0.05)
        #self.m.bluemarble()
        self.m.drawcoastlines()
        #self.m.drawmapboundary()#fill_color='aqua')
        self.m.drawstates(linewidth=self.line_states)
        self.m.drawcountries(linewidth=self.line_countries)
        #self.m.drawcountries(linewidth=0.25)
        
        #m.drawmapboundary(fill_color='aqua')

        self.m.drawmeridians(np.arange(0,360,30))
        self.m.drawparallels(np.arange(-90,90,30))
        #print(dir(m))
        
        
    
    
    def rendering_text(self):
        self.cbar.set_label(self.text_cb,y=0,ha='right',color='white')
        self.cbar.ax.set_title(f'by: {self.author}',fontweight='bold')
        
        #xn2,yn2=m(-9.52,-40.61)
        self.t = self.plt.text(-0.34,0.99,self.date_text, transform=self.ax.transAxes,
                    color='white', fontweight='bold',fontsize=14)
        self.t = self.plt.text(1.16,1,f'*\n{self.key_noaa}:\n{self.keys[self.key_noaa]}',transform=self.ax.transAxes,
                    color='grey', fontweight='bold',fontsize=5)
        self.t = self.plt.text(1.16,0.03,'data: GFS 0.25', transform=self.ax.transAxes,
                    color='white', fontweight='bold',fontsize=8)
        self.t = self.plt.text(1.18,-0.01,'NOAA/NASA', transform=self.ax.transAxes,
                    color='grey', fontweight='bold',fontsize=8)
        #t.set_bbox(dict(facecolor='red', alpha=0.81, edgecolor='black'))
        
        if self.pos_text and self.text:
            self.t = self.plt.text(self.pos_text[0],self.pos_text[1], self.text, transform=self.ax.transAxes,
                        color=self.text_color, fontweight='bold',fontsize=self.text_size)
            self.t.set_bbox(dict(facecolor='red', alpha=0.81, edgecolor='black'))
        
        # anotate data focus
        if self.annotate_text_focus and self.annotate_pos_focus:
        #    puts('writing data focus')
            xn,yn=self.m(self.annotate_pos_focus[1],self.annotate_pos_focus[0])
            self.plt.annotate(self.annotate_text_focus,
                              color=self.annotate_color_focus,
                              xy=(xn,yn),
                              fontweight=self.annotate_fontweight_focus,
                              xytext=(xn,yn),
                              xycoords='data',
                              textcoords='data')

        # anotate data focus
        if self.annotate_loc_txt and self.annotate_loc_focus:
          #  puts('writing data focus')
            xn,yn=self.m(self.annotate_loc_focus[1],self.annotate_loc_focus[0])
            self.plt.annotate(self.annotate_loc_txt,
                              color=self.annotate_loc_color,
                              xy=(xn,yn),
                              fontweight=self.fontweight_annote_loc,
                              xytext=(xn,yn),
                              xycoords='data',
                              textcoords='data')

        self.plt.title(self.title,fontweight='bold',fontsize=16)
        
        
        
    def annotate_data_focus(self,txt:str,fontsize:int=None,color:str='black',fontweight:str='bold'):
        data_city = self.dn.get_data_from_point(self.loc_focus)
        post_data = f'{(float(data_city[self.key_noaa].to_pandas()[self.indice]-self.subtr_data)):.2f}'
        self.annotate_text_focus = txt%{'data':post_data}
        self.annotate_color_focus = color
        self.annotate_fontweight_focus = fontweight
        self.annotate_pos_focus = self.loc_focus
        
        
    def annotate_data_loc(self,txt:str,loc:tuple=(40.776676,-73.971321),fontsize:int=None,color:str='black',fontweight:str='bold'):
        data_city = self.dn.get_data_from_point(loc)
        post_data = f'{((data_city[self.key_noaa].to_pandas()[self.indice]-self.subtr_data)):.2f}'
        self.annotate_loc_txt = txt%{'data':post_data}
        self.annotate_loc_color = color
        self.fontweight_annote_loc = fontweight
        self.annotate_loc_focus = loc
        
        
    def render(self,show=True,save=True):
        self.plt.style.use('dark_background')
        
       # puts('getting data ..')
        self.mining_data()
       # puts('getted data')
        
      #  puts('renderinzing plot ...')
        self.rendering_image()
        self.rendering_text()
     #   puts('renderinzed plot')
        
        if save:
         #   puts('saving plot ...')
            self.plt.savefig(self.path)
        #    puts('saved plot')
        if show:
            self.plt.show()
        self.plt.cla()
        self.plt.clf()



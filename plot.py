# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT

# very simple plot function a la matplotlib. 

# ulab.numpy should have everything so we won't need math. 
# import math as m
import ulab.numpy as np
import displayio as dsp
import terminalio     # for the font
from adafruit_display_text import label
import bitmaptools as bt

xpixels = 320
ypixels = 240

# the builtin font is 12 pixels high so we leave 16 pixels each 
# for the axis labeling    
axismargin = 16

# maximum plot area including a 1 pixel rectangular frame
ximagesize = xpixels - axismargin
yimagesize = ypixels - axismargin

# colours
palette = dsp.Palette(8)
palette[0] = 0x000000 # white / background
palette[1] = 0xFF0000 # red
palette[2] = 0x00FF00 # green
palette[3] = 0x0000FF # blue
palette[4] = 0xFFFF00 # yellow
palette[5] = 0x00FFFF # cyan
palette[6] = 0xFF00FF # purple
palette[0] = 0x000000 # white / background
palette[7] = 0x000000 # black
bgcolor = palette[0]
textcolor = palette[7]

font = terminalio.FONT
fontx, fonty = font.get_bounding_box()
xchars = ximagesize // fontx # max 304//6 = 50 characters
ychars = yimagesize // fontx # max 224//6 = 37 characters

# zoom & pan would be great but for now we can just plot with different x and y spans. 
# later: bitmaptools.rotozoom. 

def plot(f, xmin, xmax, ymin=None, ymax=None, steps=ximagesize, xsteps=8, ysteps=6, xlog=False, ylog=False):
    ''' Usage:
        f = lambda x: x**2 - 2*x -2
        plot(f, xmin, xmax, ymin=None, ymax=None, steps=ximagesize, xsteps=10, ysteps=8, xlog=False, ylog=False)
        
        f:              callable function
        xmin, xmax:     left / right x limits
        ymin, ymax:     upper / lower y limits (image may be cropped)
        steps:          number of data points in X direction (default: = x resolution)
        xsteps, ysteps: number of grid lines per axis (default: 8, 6)
        xlog:           plot x logarithmically (default False)
        ylog:           plot y logarithmically (default False)
     '''
        
    if (!callable(f)):
        raise TypeError ("first argument must be a callable function")

    # plot x log if xlog is True
    x = np.logspace (xmin, xmax, steps) if xlog is True else np.linspace (xmin, xmax, steps)
    
    y = f(x)
    
    # scale the Y axis accordingly    
    ymin = np.min(y) if ymin is None else ymin
    ymax = np.max(y) if ymax is None else ymax

    # plot y log if ylog is True
    y = np.log(y) if ylog is True else y 

    # create a root group
    plotgroup = dsp.Group()
    
    # plot area: 
    bmp = dsp.Bitmap(ximagesize, yimagesize, 8)
    plotbox = dsp.TileGrid(bmp, 
                             x = axismargin, 
                             y = 0, 
                             width = ximagesize,
                             height = yimagesize,
                             pixel_shader = palette,
                             )
    plotgroup.append(plotbox)

    # x and y axis labeling
    xlabel = label.Label(font, 
                         text = " " * xchars, 
                         color = textcolor, 
                         background_color = bgcolor) 
    xlabel.anchor = (0, 1)
    xlabelbox = dsp.TileGrid(font.bitmap, 
                              x = axismargin,
                              y = yimagesize, 
                              width = xchars,
                              height = axismargin, 
                              tile_width = fontx,
                              tile_height = fonty,
                              pixel_shader = palette,
                              )
    plotgroup.append(xlabelbox)
    
    ylabel = label.Label(font, 
                         text = " " * ychars, 
                         color = textcolor, 
                         background_color = bgcolor)  
    ylabel.anchor = (0, 1)
    ylabelbox = dsp.TileGrid(font.bitmap, 
                              x = axismargin,
                              y = yimagesize, 
                              width = ychars,
                              height = axismargin, 
                              tile_width = fontx,
                              tile_height = fonty,
                              pixel_shader = palette,
                              transpose_xy = True,
                              flip_x = True,
                              )
    plotgroup.append(ylabelbox)

    # backgrounds
    bt.fill(bmp, 0, 0, ximagesize-1, yimagesize-1)
    xs = bytes([0, ximagesize-1, ximagesize-1, 0])
    ys = bytes([0, 0, yimagesize-1, yimagesize-1])
    bt.draw_polygon(bmp, xs, ys, 7) 

    # axis labeling    
    xlabel.text = "0     1     2     3      4"
    ylabel.text = "0    1    2    3    4"



    display.root_group = plotgroup

    # here starts the function plotting
    # picture frame
    
    

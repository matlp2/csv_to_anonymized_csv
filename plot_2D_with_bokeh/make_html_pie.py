

from math import pi

import pandas as pd

import bokeh
import bokeh.palettes
import bokeh.plotting
import bokeh.transform
import bokeh.embed
import bokeh.resources


def html_of_pie(
		data_frame,
		args_figure = dict(),
		args_wedge = dict(),
	):

	x = dict(zip(data_frame.iloc[:,0], data_frame.iloc[:,1]))

	data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'nom1'})
	data['angle'] = data['value']/data['value'].sum() * 2*pi
	#data['color'] = bokeh.palettes.Category20c[len(x)]
	data['color'] = bokeh.palettes.viridis(len(data['value']))

	plot =  bokeh.plotting.figure(
		**{
			'height':350,
			#title="Pie Chart",
			'toolbar_location':None,
			'tools':"hover",
			'tooltips':"@nom1: @value",
			'x_range':(-0.5, 1.0),
			**args_figure,
		}
	)

	plot.wedge(
		**{
			'x':0,
			'y':1,
			'radius':0.4,
			'start_angle':bokeh.transform.cumsum('angle', include_zero=True),
			'end_angle':bokeh.transform.cumsum('angle'),
			'line_color':"white",
			'fill_color':'color',
			'legend_field':'nom1',
			'source':data,
			**args_wedge,
		}
	)

	plot.axis.axis_label = None
	plot.axis.visible = False
	plot.grid.grid_line_color = None


	return bokeh.embed.file_html(plot, bokeh.resources.CDN, "my plot")

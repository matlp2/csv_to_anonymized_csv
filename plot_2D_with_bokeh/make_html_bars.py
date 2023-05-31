# commande: (cd plot_2D_with_bokeh && python3 make_html_bars.py && chromium bars.html)
# parenthèses pour que le cd soit temporaire (parentheses => subshell)



from math import pi

import pandas as pd

import bokeh
import bokeh.palettes
import bokeh.plotting
import bokeh.transform
import bokeh.embed
import bokeh.resources
import bokeh.models


def html_of_bars(
		data_frame,
		args_figure = dict(),
		args_vbar = dict(),
		nom_axe_x = 'nom_axe_x'
	):
	
	x_keys = data_frame.iloc[:,0]
	x_vals = data_frame.iloc[:,1]


	source = bokeh.models.ColumnDataSource(data={nom_axe_x:x_keys, 'counts':x_vals})

	plot = bokeh.plotting.figure(
		**{
			'x_range':x_keys,
			'width':1000,
			'toolbar_location':None,
			**args_figure
		}
		#x_range=x_keys,
		##height=250,
		#width = 1000,
		##title="Fruit Counts by Year",
		#toolbar_location=None,
		##tools="hover",
		##tooltips="$name @fruits: @$name"
		#**input['args_figure']
	)

	plot.vbar(
		**{
			'x': nom_axe_x,
			'top': 'counts',
			'width': 0.9,
			'source': source,
			'legend_field': nom_axe_x,
			'line_color': 'white',
			'fill_color': bokeh.transform.factor_cmap(
				nom_axe_x,
				palette=bokeh.palettes.viridis(len(x_vals)),
				factors=x_keys
			),
			**args_vbar
		}
		#x='fruits',
		#top='counts',
		#width=0.9,
		#source=source,
		#legend_field="fruits",
    	#line_color='white',
		#fill_color = bokeh.transform.factor_cmap(
		#	'fruits',
		#	palette=bokeh.palettes.viridis(len(x_vals)),
		#	factors=x_keys
		#),
		#**input['args_vbar']
	)

	plot.xgrid.grid_line_color = None
	#plot.y_range.start = 0
	#plot.y_range.end = 9
	plot.legend.orientation = "horizontal"
	plot.legend.location = "top_center"

	#plot.y_range.start = 0
	#plot.x_range.range_padding = 0.1
	plot.xgrid.grid_line_color = None
	plot.axis.minor_tick_line_color = None
	plot.outline_line_color = None

	#bokeh.plotting.show(p)


	return bokeh.embed.file_html(plot, bokeh.resources.CDN, "my plot")


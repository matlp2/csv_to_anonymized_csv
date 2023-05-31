
# command:
# ((cat conf.json | python3 convert_csv_to_html_pie_chart.py) && (chromium result.html)) &

import sys
#sys.path.append('..')
from my_html import *

import json
from itertools import islice
from itertools import count

import os


# don't take lines with comments (otherwise json.load(sys.stdin.read()))
#json_text = ''.join(filter(
#		lambda line : not line.strip(' \t\n').startswith('#'),
#		sys.stdin.readlines()))

#print('json_text =', json_text)

#input_json = json.loads(json_text)
input_json = json.loads(sys.stdin.read())




print(input_json)


script_input = 'input_data = ['

import csv
import random
with open(input_json['src']['path'], newline='') as f:
	#spamreader = csv.reader(f, delimiter=' ', quotechar='|')
	rows = csv.reader(
		f,
		delimiter = input_json['src'].get('delimiter',';'),
		**({'quotechar': input_json['src']['quotechar']} if 'quotechar' in input_json['src'] else dict())
	)

	header = next(rows)


	


	for row in rows:
		script_input += f'''
		{{
			'name' : {repr(str(row[0]))},
			'quantity': {float(row[1])},
			//'color': new Float32Array([0,1,1,1])
			'color': new Float32Array([{random.random()},{random.random()},{random.random()},1])
		}},'''
		print(', '.join(row))





script_input += '\n]'

print(script_input)


with block('html'):

	with block('header'):

		html += '<meta charset="UTF-8">'

	#with block('body', 'style="width:100%;height:100%;padding:0;margin:0"'):
	#with block('html'):
	#with block('body', 'style="width:100%;height:100%;margin:0"'):
	disable_horizontal_scroll = "max-width:100%;overflow-x:hidden;"
	disable_vertical_scroll = "overflow-y:hidden;"

	with block('body', f'style="margin:0; {disable_vertical_scroll} {disable_horizontal_scroll}"'):#  overflow-y: hidden; pour ne pas avoir de scroll-bar verticale

		#html.s += '''
		#	<input type="color" value="#ff0000" />
		#	'''

		
		
		
		with block('div', 'class="wrapper" id="superposition"'):

			

			with block('style'):
				html += '''
	.wrapper {
		position: relative;
		width: 100%;
		height: 100%;
	}
	.wrapper canvas {
		position: absolute;
		top: 0;
		left: 0;
	}'''

			

			
			#with block('canvas', 'width = 100% height = 100% id = "my_Canvas"'):
			# "pointer-events: none;" pour que les events passent à tavers le canvas pour pouvoir cliquer sur les btn de changement de couleur
			with block('canvas', 'style="width:100%;height:100%;pointer-events: none;" id = "my_3d_canvas"'):
			#with block('canvas', 'style="" id = "my_Canvas"'):
				pass

			# "pointer-events: none;" pour que les events passent à tavers le canvas pour pouvoir cliquer sur les btn de changement de couleur
			with block('canvas', 'style="width:100%;height:100%;pointer-events: none;" id = "my_2d_canvas"'):
				pass

			with block('script'):
				html += script_input
				


			#with block('script', 'src = "script.js"'):
			#	pass

		center_style = 'style="display:block;margin-left:auto;margin-right:auto"'


		


		


		with block('div', 'id = "options_panel" style="background-color:rgba(255, 255, 255, .7)"'):

			with block('table', ' width=100%'):
				with block('tr'):

					with block('td'):
						with block('button', f'onclick="save_image()" {center_style}'):
							with block('text'):
								html += "télécharger l'image"

					
					with block('td'):
						with block('button', f'onclick="randomise_colors()" {center_style}'):
							with block('text'):
								html += "coleurs au hasard"

					with block('td'):
						with block('button', f'onclick="switch_trier_input_data()" {center_style}'):
							with block('text'):
								html += "trier"

					with block('td'):
						with block('center'):
							#with block('table', ' width=100%'):
							with block('table'):

								with block('tr', 'onclick="switch_see_labels()"'):
									with block('td', f'{center_style}'):
										with block('center'):
											with block('div', f'onclick=""'):
												with block('input', 'type="checkbox" checked id="checkbox_see_labels"'):
													#html += "afficher les labels"
													pass
									with block('td'):
										html += "labels"

								with block('tr','onclick="switch_voir_pourcentages()"'):
									with block('td', f'{center_style}'):
										with block('center'):
											with block('div', f'onclick=""'):
												with block('input', 'type="checkbox" checked id="checkbox_voir_pourcentages" style="pointer-events:none;"'):
													#html += "afficher les pourcentages"
													pass
									with block('td'):
										html += "pourcentages"

								with block('tr', f'onclick="switch_voir_qté()"'):
									#with block('td', f'onclick="document.getElementById(\'checkbox_voir_qté\').checked ^= 1;" {center_style}'):
									with block('td', f'{center_style}'):
										with block('center'):
											with block('div', f'onclick=""'):
												#with block('input', 'type="checkbox" checked id="checkbox_voir_qté"'):
												with block('input', 'type="checkbox" checked id="checkbox_voir_qté" style="pointer-events:none;"'):
													#html += "afficher les qté"
													pass
									with block('td'):
										html += "qté"

			with block('table', ' width=100%'):
				with block('tr'):

					def make_slider(description, range_name):
						global html
						#with block('div', 'class="column"'):
						with block('td'):
							with block('p',f'id="nom_{range_name}" style="text-align:center"'):
								html += description
							with block('input', f'type="range" id="{range_name}" min="0" max="1" step=".001" style="display:block;margin-left:auto;margin-right:auto"'):
								pass

					
					make_slider('rayon interne', 'range_rayon_interne_ratio')
					make_slider('rayon', 'range_rayon')
					make_slider('separation', 'range_separate_pieces')
					make_slider('hauteur', 'range_hauteur')
					make_slider('ombre', 'range_ombre')
					make_slider('others threshold', 'range_others_threshold')
					make_slider('alpha fond', 'range_bg_alpha')

					with block('td'):
						with block('p','style="text-align:center"'):
							html += 'couleur fond'
						with block('input', 'type="color" id="color_bg" style="display: block;margin-left: auto; margin-right: auto"'):
							pass

					make_slider('rayon labels', 'range_rayon_labels')
					make_slider('taille labels', 'range_taille_labels')

					

			with block('center'):
				html += 'cliquez sur les les labels pour changer les couleurs'


		if False:
			html += '''
			<canvas
				style="
				top:100%;
				position: absolute;
				background-color: rgba(255, 0, 0, 0.8);
				width:100%;
				height:25%;
				"

				id = "options_panel"
			>
			</canvas>
			'''
		


		


		

		html += '''
		<canvas
			style="
			/*right:10%;*/
			left:50%;
			transform: translate(-50%, 0%);
			bottom:0%;

			/*width:5%;
			height:5%;*/
			position: absolute;
			/*background-color:rgba(255, 0, 0, 0.8);*/
			background-color:rgba(0, 0, 0, 0);
			"
			id = "btn_expand"
		>	
		</canvas>
		'''
			
		html += '''
			<script>
				log = console.log
				superposition = document.getElementById("superposition")
				options_panel = document.getElementById("options_panel")
				btn_expand = document.getElementById("btn_expand")


				nb_click_on_btn_expand = 0
				
				maj_image_btn_expand = () => {
					var ctx = btn_expand.getContext("2d")
					const w = parseFloat(btn_expand.clientWidth)
					const h = parseFloat(btn_expand.clientHeight)
					//ctx.clearRect(0, 0, w, h)
					//ctx.fillStyle = "rgba(0,0,0,0)"
					//ctx.fillStyle = "green";
					//ctx.fillRect(0, 0, w, h)
					ctx.clearRect(0, 0, w, h)
					ctx.lineWidth = .08*w;
					ctx.strokeStyle = "rgba(200,200,200,.5)";
					ctx.beginPath();
					ctx.arc(w/2, h/2, (w - ctx.lineWidth)/2, 0, 2 * Math.PI);
					ctx.stroke();

					ctx.beginPath();
					var vers_le_haut = (nb_click_on_btn_expand % 2 == 0)
					ctx.lineTo(.2*w, (vers_le_haut ? (1-.35) : .35)*h);
					ctx.lineTo(.5*w, (vers_le_haut ? (1-.65) : .65)*h);
					ctx.lineTo(.8*w, (vers_le_haut ? (1-.35) : .35)*h);
					ctx.stroke();
				}

				maj_wh_btn_expand = () => {
					var l = Math.min(30, Math.min(.25*superposition.clientWidth, .25*superposition.clientHeight))
					btn_expand.style.width = l+"px"
					btn_expand.style.height = l+"px"
					btn_expand.clientWidth = l
					btn_expand.clientHeight = l
					btn_expand.width = l
					btn_expand.height = l
					maj_image_btn_expand()
				}


				
				//ctx.globalAlpha = 0.5


				btn_expand.onclick = () => {
					log('CLICK on btn_expand')

					steps = [
						{ transform: 'translateY('+(nb_click_on_btn_expand++%2 == 1 ? '0px' : '-'+options_panel.clientHeight+'px') },
					]

					options = {
						duration: 300,
						iterations: 1,
						fill: 'forwards',
					}

					options_panel.animate(
						steps,
						options
					);

					btn_expand.animate(
						steps,
						options
					);
					
					maj_image_btn_expand()
				}

				fade_timeout = null
				fade = null
				window.addEventListener('mousemove', () => {
					btn_expand.style.opacity = "1";
					if(fade_timeout !== null) clearTimeout(fade_timeout)
					fade_timeout = setTimeout(
						()=>{
							if(fade !== null) clearInterval(fade);
							fade = setInterval(() => {
								//log('FADING')
								btn_expand.style.opacity = Math.max(0, btn_expand.style.opacity-.015); // 500 milliseconds
								if (btn_expand.style.opacity <= 0) {
										clearInterval(fade);
										fade = null
								}
						},
						10);
						},
						1000
					)
				})

				maj_wh_btn_expand()

				window.addEventListener('resize', (ev) => {
					maj_wh_btn_expand()
				}, true);
			</script>
			'''

		with open('script.js', 'r') as f:
			script = f.read()
			
			if True: #compress and remove comments

				print(len(script))

				script = script.replace('\t', '')
				#script = script.replace('\n\n', '\n')
				#script = script.replace('\n\n', '\n')

				# remove comments and empty lines
				script_no_comments = ''
				for line in script.splitlines():
					if len(line) > 0 and not line.strip(' ').startswith('//'):
						script_no_comments += line + '\n'

				script = script_no_comments



				def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
					return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

				for c, nom in zip(count(),[
					'set_my_rotation_to_my_rotation_mult_your_rotation',
					'set_my_rotation_to_your_rotation_mult_my_rotation',
					'make_pie_piece',
					'cpu_object',
					'to_gpu_object',
					'gpu_object',
					'Vertices',
					'vertex_buffer',
					'index_buffer',
					'color_buffer',
					'normal_buffer',
					'index_count',
					'vertices',
					'indexes',
					#'colors',
					'normals',
					'set_vao',
					'display',
					'set_p',
					'get_p',
					'set_rot',
					'rotate_around_the_x_axis',
					'rotate_around_the_y_axis',
					'get_invert',
					'get_image_pos',
					'mult_mat4_vec4',
					'Hold_clic',
					'animate',
					'Base',
					'your_rotation',
					'result_rotation',
					'angle_radiants',
					'angle',
					'a_key_is_pressed',
					'pressedKeys',
					'ctx_2d',
					'request_animation_frame',
					'animationFrameRequested',
					'update_wh',
					'resizeCanvasToDisplaySize',
					#'pie',
					'sum',
					'translated_copy',
					'translate',
					'P_inv',
					'aspect',
					'near',
				]): 
					#script = script.replace(nom, f'I{c:x}')
					script = script.replace(nom, f'I{baseN(c, 62)}')


				#script = script.replace('\n\n', ' ')
				#script = script.replace('\n\n', ' ')

				print(len(script))
			

			with block('script'):
				html.s += script

			

		folder_path_of_this_py_file = os.path.dirname(os.path.abspath(__file__)).replace('"','\"')
		#with block('iframe', f'src="{folder_path_of_this_py_file}/options_on_top/options_on_top.html" style="border:none;position:absolute;top:0%;left:0%;width:100%;height:100%;pointer-events:none;"'):
		#	pass

		#with block('script', f'src="{folder_path_of_this_py_file}/options_on_top/options_on_top.js"'):
		with block('script'):
			with open(f"{folder_path_of_this_py_file}/options_on_top/options_on_top.js", 'r') as f:
				html += f.read()

		with block('script'):
			html += '''
			make_options_on_top(
				document.getElementById('superposition'),
				switch_to_vertical_bars,
				switch_to_horizontal_bars,
				switch_to_pie,
				save_image,
				switch_projection_matrix
			)
			'''



html.save(input_json['dst'])



'''
input_data = [
	{
		'name' : 'water',
		'quantity': 50,
		'color': new Float32Array([0,1,1,1])
	},
	{
		'name' : 'fire',
		'quantity': 23,
		'color': new Float32Array([1,0,0,.5])
	},
	{
		'name' : 'earth',
		'quantity': 5,
		'color':new Float32Array([0,0.2,0,1])
	},
	{
		'name' : 'A',
		'quantity': 30,
		'color': new Float32Array([1,0,1,1])
	},
	{
		'name' : 'graines',
		'quantity': 23,
		'color': new Float32Array([.1,.3,.5,1])
	},
	{
		'name' : 'gravier',
		'quantity': 22,
		'color': new Float32Array([0,0,0,1])
	},
	{
		'name' : 'verre',
		'quantity': 31,
		'color': new Float32Array([.6,.25,.2,1])
	},
	{
		'name' : 'void',
		'quantity': 0.01,
		'color': new Float32Array([.1,.1,0,1])
	},
	{
		'name' : 'G',
		'quantity': 11,
		'color': new Float32Array([.6,.5,.7,1])
	},
	{
		'name' : 'H',
		'quantity': 21,
		'color': new Float32Array([.4,.2,.8,.5])
	},
	{
		'name' : 'air',
		'quantity': 21,
		'color': new Float32Array([.1,.3,1,.2])
	},
]'''



const scale_options_on_top = .08;


const _list_fade_out_callbacks = []

var cursor_on_options_on_tops = false


const fade_out_if_cursor_does_not_move = (elm) => {

	var fade_timeout = null
	var fade = null

	var callback = () => {

		elm.style.opacity = "1";

		if(fade_timeout !== null) clearTimeout(fade_timeout)

		fade_timeout = setTimeout(
			()=>{
				if(cursor_on_options_on_tops) return
				if(fade !== null) clearInterval(fade);
				fade = setInterval(() => {
					//log('FADING')
					elm.style.opacity = Math.max(0, elm.style.opacity-.015)
					if (elm.style.opacity <= 0) {
						clearInterval(fade)
						fade = null
					}
				},
				10
			)
			},
			900
		)
	}

	_list_fade_out_callbacks.push(callback)

	window.addEventListener('mousemove', callback, false)
}


const apply_style_of_btn_options_on_top = (btn, f_click=()=>{console.log('click options_on_top')}) => {
	btn.style.position = 'absolute'
	btn.style.top = '40px'
	btn.style.left = '40px'
	btn.style.cursor = 'pointer'
	btn.style['background-color'] = 'rgb(255, 255, 255, .2)'
	btn.addEventListener('click', f_click)
	fade_out_if_cursor_does_not_move(btn)

	btn.addEventListener('mouseenter', (ev) => {
		cursor_on_options_on_tops = true
	})
	btn.addEventListener('mouseleave', (ev) => {
		cursor_on_options_on_tops = false
	})
}


const make_options_on_top = (
	sup,
	f_click_btn_switch_to_bars = ()=>{console.log('f_click_btn_switch_to_bars')},
	f_click_btn_switch_to_horizontal_bars = ()=>console.log('f_click_btn_switch_to_horizontal_bars'),
	f_click_btn_switch_to_pie = ()=>{console.log('f_click_btn_switch_to_pie')},
	f_click_btn_photo = ()=>{console.log('f_click_btn_photo')},
	f_click_btn_switch_projection_matrix = ()=>{console.log('f_click_btn_switch_projection_matrix')},
) => {

	sup.style.position = 'relative'

	{// btn_switch_to_bars

		const btn_switch_to_bars = document.createElement('canvas')
		apply_style_of_btn_options_on_top(btn_switch_to_bars, f_click_btn_switch_to_bars)
		sup.appendChild(btn_switch_to_bars)

		const maj_btn_switch_to_bars = () => {

			console.log('maj_btn_switch_to_bars ' + window.innerWidth + ' ' + window.innerHeight)
			const ctx = btn_switch_to_bars.getContext('2d')
			const client_size = scale_options_on_top*Math.min(window.innerWidth, window.innerHeight)
			btn_switch_to_bars.clientWidth = client_size
			btn_switch_to_bars.clientHeight = client_size
			const size = window.devicePixelRatio * client_size
			const w = btn_switch_to_bars.width = size
			const h = btn_switch_to_bars.height = size
			btn_switch_to_bars.style.top = .2*size + 'px'
			btn_switch_to_bars.style.left = .2*size + 'px'
			btn_switch_to_bars.style['border-radius'] = .2*size + 'px'


			
			const nb_bar = 4.0

			const size_inner = .7*size

			const padding = .5*(size-size_inner)
			
			const ecart = .15*size_inner/nb_bar

			const w_bar = size_inner/nb_bar - 2*ecart

			for(var c = 0; c < nb_bar; ++c) {
				const x = padding + c*(w_bar + 2*ecart) + ecart
				const X = x + w_bar
				const y = padding + Math.random()*size_inner
				const Y = padding + size_inner

				const run_path = () => {
					ctx.beginPath()
					ctx.moveTo(x, y)
					ctx.lineTo(x, Y)
					ctx.lineTo(X, Y)
					ctx.lineTo(X, y)
					ctx.closePath()
				}

				const color =
					[
						parseInt(255*Math.random()),
						parseInt(255*Math.random()),
						parseInt(255*Math.random()),
					]

				run_path()
				ctx.lineWidth = .03*size
				ctx.strokeStyle = 'rgb('+.4*color[0]
									+','+.4*color[1]
									+','+.4*color[2]
									+')'
				ctx.stroke()


				run_path()
				ctx.fillStyle = 'rgb('+color[0]
									+','+color[1]
									+','+color[2]
									+')'
				ctx.fill()
			}

		}
		maj_btn_switch_to_bars()
		window.addEventListener('resize', maj_btn_switch_to_bars, true);

	}



	{// btn_switch_to_horizontal_bars

		const btn_switch_to_horizontal_bars = document.createElement('canvas')
		apply_style_of_btn_options_on_top(btn_switch_to_horizontal_bars, f_click_btn_switch_to_horizontal_bars)
		sup.appendChild(btn_switch_to_horizontal_bars)

		const maj_btn_switch_to_horizontal_bars = () => {

			console.log('maj_btn_switch_to_horizontal_bars ' + window.innerWidth + ' ' + window.innerHeight)
			const ctx = btn_switch_to_horizontal_bars.getContext('2d')
			const client_size = scale_options_on_top*Math.min(window.innerWidth, window.innerHeight)
			btn_switch_to_horizontal_bars.clientWidth = client_size
			btn_switch_to_horizontal_bars.clientHeight = client_size
			const size = window.devicePixelRatio * client_size
			const w = btn_switch_to_horizontal_bars.width = size
			const h = btn_switch_to_horizontal_bars.height = size
			btn_switch_to_horizontal_bars.style.top = .2*size + 'px'
			btn_switch_to_horizontal_bars.style.left = (.2 + 1 +.2)*size + 'px'
			btn_switch_to_horizontal_bars.style['border-radius'] = .2*size + 'px'


			
			const nb_bar = 4.0

			const size_inner = .7*size

			const padding = .5*(size-size_inner)
			
			const ecart = .15*size_inner/nb_bar

			const w_bar = size_inner/nb_bar - 2*ecart

			for(var c = 0; c < nb_bar; ++c) {
				const x = padding + c*(w_bar + 2*ecart) + ecart
				const X = x + w_bar
				const y = padding + Math.random()*size_inner
				const Y = padding + size_inner

				const run_path = () => {
					ctx.beginPath()
					ctx.moveTo(size - y, x)
					ctx.lineTo(size - Y, x)
					ctx.lineTo(size - Y, X)
					ctx.lineTo(size - y, X)
					ctx.closePath()
				}

				const color =
					[
						parseInt(255*Math.random()),
						parseInt(255*Math.random()),
						parseInt(255*Math.random()),
					]

				run_path()
				ctx.lineWidth = .03*size
				ctx.strokeStyle = 'rgb('+.4*color[0]
									+','+.4*color[1]
									+','+.4*color[2]
									+')'
				ctx.stroke()


				run_path()
				ctx.fillStyle = 'rgb('+color[0]
									+','+color[1]
									+','+color[2]
									+')'
				ctx.fill()
			}

		}
		maj_btn_switch_to_horizontal_bars()
		window.addEventListener('resize', maj_btn_switch_to_horizontal_bars, true)

	}


	{//btn_switch_to_pie

		const btn_switch_to_pie = document.createElement('canvas')
		apply_style_of_btn_options_on_top(btn_switch_to_pie, f_click_btn_switch_to_pie)

		sup.appendChild(btn_switch_to_pie)
		
		const newton = (
				f /* from x,y to scalar */,
				x_start,
				y_start,
				dist_to_zero_break,
				nb_loops_max = 200
			) => {
				
				var x = x_start
				var y = y_start
				
				for(var c = 0; c < nb_loops_max; ++c) {

					const fxy = f(x,y)

					if (Math.abs(fxy) <= dist_to_zero_break) {
						break
					}

					const dx = .0001
					const dy = .0001
					

					var df_x = f(x+.5*dx,y) - f(x-.5*dx,y)
					var df_y = f(x,y+.5*dy) - f(x,y-.5*dy)
					const df_min = .5*dist_to_zero_break

					/*dfx_sur_dx = df_x/dx
					dfy_sur_dy = df_y/dy*/
					
					if (Math.abs(df_x) < df_min) df_x = (df_x > 0 ? 1 : -1)*df_min
					if (Math.abs(df_y) < df_min) df_y = (df_y > 0 ? 1 : -1)*df_min

					x -= .5*(dx/df_x)*fxy
					y -= .5*(dy/df_y)*fxy

					/*x -= .5*fxy/dfx_sur_dx
					y -= .5*fxy/dfy_sur_dy*/
				}

				return [x, y]
			}


			const maj_btn_switch_to_pie = () => {
				console.log('maj_btn_switch_to_pie ' + window.innerWidth + ' ' + window.innerHeight)
				const ctx = btn_switch_to_pie.getContext('2d')
				const client_size = scale_options_on_top*Math.min(window.innerWidth, window.innerHeight)
				btn_switch_to_pie.clientWidth = client_size
				btn_switch_to_pie.clientHeight = client_size
				const size = window.devicePixelRatio * client_size
				const w = btn_switch_to_pie.width = size
				const h = btn_switch_to_pie.height = size
				btn_switch_to_pie.style.top = (1.+.2+.2)*size + 'px'
				btn_switch_to_pie.style.left = .2*size + 'px'
				btn_switch_to_pie.style['border-radius'] = .2*size + 'px'

				const nb_bar = 5.0

				var quatities = []
				var total_quatity = parseFloat(0)
				for(var c = 0; c < nb_bar; ++c) {
					quatity = Math.max(Math.random(), .01)
					total_quatity += quatity
					quatities.push(quatity)
				}
				var ponds = []

				for(var c = 0; c < nb_bar; ++c) {
					ponds.push(quatities[c]/total_quatity)
				}

				const size_inner = .7*size

				const padding = .5*(size-size_inner)
				
				const ecart = .09*2*Math.PI/nb_bar

				//const da = 2*Math.PI/nb_bar - 2*ecart
				const da = 2*Math.PI

				//var a = Math.random()*2*Math.PI
				var a = 0

				const R = .5*size_inner
				const cx = .5*w
				const cy = .5*h

				// intersection de deux droites qui marche même si parallèle
				const f_intersection = (
					x1,
					y1,
					// d1 doit être unitaire
					dx1,
					dy1,

					x2,
					y2,
					// d2 doit être unitaire
					dx2,
					dy2,

					/*dist_stop,
					nb_max_iter = 100*/
				) => {

					const dist_for_intersection_to_nullify = (x, y) => {
						const dist1 = Math.abs((x-x1)*dy1 - (y-y1)*dx1)
						const dist2 = Math.abs((x-x2)*dy2 - (y-y2)*dx2)
						return Math.max(dist1, dist2)
					}

					return dist_for_intersection_to_nullify
					
					/*
					plus ange faible, le plus d'itération sont necessaires
					probleme si angle 
					for(var c = 0; c < nb_max_iter; ++c) {

						// milieu
						const x = .5*(x1+x2)
						const y = .5*(y1+y2)

						// distance du milieu à droite 1
						const dist1 = Math.abs((x-x1)*dy1 - (y-y1)*dx1)

						// distance du milieu à droite 2
						const dist2 = Math.abs((x-x2)*dy2 - (y-y2)*dx2)

						if (Math.max(dist1, dist2) < dist_stop) {
							break
						}

						// p1 = projeter milieu sur 1
						const scalar1 = (x-x1)*dx1 + (y-y1)*dy1
						x1 = x1 + scalar1*dx1
						y1 = y1 + scalar1*dy1

						// p2 = projeter milieu sur 2
						const scalar2 = (x-x2)*dx2 + (y-y2)*dy2
						x2 = x2 + scalar2*dx2
						y2 = y2 + scalar2*dy2
					}
					
					return [.5*(x1+x2),.5*(y1+y2)]
					*/
				}

				for(var c = 0; c < nb_bar; ++c) {
					//const a = c*(da + 2*ecart) + ecart
					//const a = c*da
					const A = Math.min(a + 2*Math.PI*ponds[c], 2*Math.PI)
					const y = padding + Math.random()*size_inner
					const Y = padding + size_inner

					const run_path = () => {
						ctx.beginPath()
						
						const da = A-a
						const a_padding = Math.min(.09*da, .018*2*Math.PI)
						//if (da < Math.PI)
						{
							
							//const r = .05*size_inner

							/*const ua = [
								R*Math.cos(a),
								R*Math.sin(a)
							]

							const uA = [
								R*Math.cos(A),
								R*Math.sin(A)
							]

							const i = intersection(

								R*Math.cos(a+a_padding),
								R*Math.sin(a+a_padding),
								Math.cos(a),
								Math.sin(a),

								R*Math.cos(A-a_padding),
								R*Math.sin(A-a_padding),
								Math.cos(A),
								Math.sin(A),

								.01
							)*/

							const i = newton(
								f_intersection(

									R*Math.cos(a+a_padding),
									R*Math.sin(a+a_padding),
									Math.cos(a),
									Math.sin(a),

									R*Math.cos(A-a_padding),
									R*Math.sin(A-a_padding),
									Math.cos(A),
									Math.sin(A),

									//.01
								),
								0,
								0,
								.01,
								200
							)

							//console.log(i)

							//const u1 = .1
							
							const r = 2.*R*a_padding*Math.cos(da/2.)
							//const x = .5*w + r*Math.cos(.5*(a+A))
							const x = .5*w + i[0]
							//const y = .5*h + r*Math.sin(.5*(a+A))
							const y = .5*h + i[1]
							ctx.moveTo(x,y)
							//ctx.arc(x, y, R, a+a_padding, A-a_padding, false)
							ctx.arc(cx, cy, R, a+a_padding, A-a_padding, false)
							//ctx.arc(.5*w, .5*h, .2*R, A-a_padding, a+a_padding, true)
						}
						/*else{
							const x = .5*w
							const y = .5*h
							ctx.moveTo(x,y)
							//ctx.arc(x, y, R, a+a_padding, A-a_padding, false)
							ctx.arc(x, y, R, a+a_padding, A-a_padding, false)
						}*/
						
						ctx.closePath()
					}

					run_empty_circle = ()=>{
						ctx.beginPath()
						ctx.arc(cx, cy, .4*R, 0, 2*Math.PI, false)
						ctx.closePath()
					}

					const color =
						[
							parseInt(255*Math.random()),
							parseInt(255*Math.random()),
							parseInt(255*Math.random()),
						]

					
					run_path()
					ctx.lineWidth = .03*size
					ctx.lineCap = 'butt'
					ctx.strokeStyle = 'rgb('+.4*color[0]
										+','+.4*color[1]
										+','+.4*color[2]
										+')'
					ctx.stroke()


					run_path()
					ctx.fillStyle = 'rgb('+color[0]
										+','+color[1]
										+','+color[2]
										+')'
					ctx.fill()

					

					a = A
				}

				run_empty_circle()
				//ctx.globalAlpha = 0;
				
				ctx.globalCompositeOperation = 'destination-out'
				ctx.fillStyle = 'rgba(0,0,0,1)'
				ctx.fill()
				//ctx.globalAlpha = 1.;
				ctx.globalCompositeOperation = "source-over" // reset default

			}
			maj_btn_switch_to_pie()
			window.addEventListener('resize', maj_btn_switch_to_pie, true);

	}



	{ // btn_photo

		const btn_photo = document.createElement('canvas')
		apply_style_of_btn_options_on_top(btn_photo, f_click_btn_photo)
		sup.appendChild(btn_photo)

		const maj_btn_photo = () => {

			const ctx = btn_photo.getContext('2d')
			const client_size = scale_options_on_top*Math.min(window.innerWidth, window.innerHeight)
			btn_photo.clientWidth = client_size
			btn_photo.clientHeight = client_size
			const size = window.devicePixelRatio * client_size
			const w = btn_photo.width = size
			const h = btn_photo.height = size
			btn_photo.style.top = (1.+.2+.2+1.+.2)*size + 'px'
			btn_photo.style.left = .2*size + 'px'
			btn_photo.style['border-radius'] = .2*size + 'px'



			const size_inner = .7*size
			const padding = .5*(size - size_inner)
			const h_ap = .7*size_inner
			const w_ap = size_inner
			const x = .5*(size - w_ap)
			const X = x + w_ap
			const cx = .5*(x+X)
			const y = .5*(size - h_ap)
			const Y = y + h_ap
			const cy = .5*(y+Y)


			const run_rec = () => {
				ctx.beginPath()
				ctx.moveTo(x, y)
				ctx.lineTo(x, Y)
				ctx.lineTo(X, Y)
				ctx.lineTo(X, y)
				const d1 = .2*w_ap
				const d2 = .05*w_ap
				const dy = .12*size_inner
				ctx.lineTo(X-d1,y)
				ctx.lineTo(X-d1-d2,y-dy)
				ctx.lineTo(x+d1+d2,y-dy)
				ctx.lineTo(x+d1,y)
				ctx.closePath()
			}

			

			run_rec()
			ctx.fillStyle = 'rgba(20,20,20,1)'
			ctx.fill()


			line_width = .04*size

			const run_circle = () => {
				ctx.beginPath()
				ctx.arc(cx, cy, .41*Math.min(h_ap, h_ap) - .5*line_width, 0, 2*Math.PI, false)
				ctx.closePath()
			}

			run_circle()
			ctx.lineWidth = line_width
			ctx.strokeStyle = 'rgba(255,255,255,.4)'
			ctx.stroke()

		}

		maj_btn_photo()
		
		window.addEventListener('resize', maj_btn_photo, true)
	}


	{ // btn_switch_projection_matrix

		const btn_switch_projection_matrix = document.createElement('canvas')
		
		sup.appendChild(btn_switch_projection_matrix)
		var projection = '3D'

		

		const maj_btn_switch_projection_matrix = () => {

			const ctx = btn_switch_projection_matrix.getContext('2d')
			const client_size = scale_options_on_top*Math.min(window.innerWidth, window.innerHeight)
			btn_switch_projection_matrix.clientWidth = client_size
			btn_switch_projection_matrix.clientHeight = client_size
			const size = window.devicePixelRatio * client_size
			const w = btn_switch_projection_matrix.width = size
			const h = btn_switch_projection_matrix.height = size
			btn_switch_projection_matrix.style.top = (.2 + 1 + .2 + 1 + .2 + 1 + .2)*size + 'px'
			btn_switch_projection_matrix.style.left = .2*size + 'px'
			btn_switch_projection_matrix.style['border-radius'] = .2*size + 'px'

			
			ctx.font = .7*size + 'px serif'
			const mes = ctx.measureText(projection)
			ctx.fillText(projection, .5*(size-mes.width), .74*size)
		}

		apply_style_of_btn_options_on_top(btn_switch_projection_matrix, (ev) => {
			f_click_btn_switch_projection_matrix(ev)
			if(projection == '3D') {
				projection = '2D'
			} else{
				projection = '3D'
			}
			maj_btn_switch_projection_matrix()
		})

		maj_btn_switch_projection_matrix()



		window.addEventListener('resize', maj_btn_switch_projection_matrix, true)

		

		
	}


}


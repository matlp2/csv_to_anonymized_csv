log = console.log
sin = Math.sin
cos = Math.cos
min = Math.min
max = Math.max
abs = Math.abs
exp = Math.exp
sqrt = Math.sqrt
round = Math.round
PI = Math.PI



//https://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
componentToHex = (c) => {
	var hex = c.toString(16);
	return hex.length == 1 ? "0" + hex : hex;
}
rgbToHex = (r, g, b) => {
	return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
hexToRgb = (hex) => {
	var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
	return result ? [
		parseInt(result[1], 16),
		parseInt(result[2], 16),
		parseInt(result[3], 16)
	] : null;
}



var canvas = document.getElementById('my_3d_canvas');
gl = canvas.getContext('webgl2');

var canvas_2d = document.getElementById('my_2d_canvas');
const ctx_2d = canvas_2d.getContext("2d");





class Vertices extends Float32Array {

	constructor(n = 0) {
		super(3*n)
	}

	set_p(i, x, y, z) {
		this[3*i + 0] = x
		this[3*i + 1] = y
		this[3*i + 2] = z

	}

	get vertex_count() {
		return this.length/3
	}

}

class gpu_object{

	constructor() {
		this.vao = gl.createVertexArray();
		this.vertex_buffer = gl.createBuffer();
		this.index_buffer = gl.createBuffer();
		this.color_buffer = gl.createBuffer();
		//this.normal_buffer = gl.createBuffer();
		this.index_count = 0
	}

	set_vertices(vertices){
		if (!(vertices instanceof Float32Array)) throw new Error('vertices must be Float32Array');
		gl.bindBuffer(gl.ARRAY_BUFFER, this.vertex_buffer);
		gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.DYNAMIC_DRAW);
		gl.bindBuffer(gl.ARRAY_BUFFER, null);
	}

	set_indexes(indexes){
		if (!(indexes instanceof Uint16Array)) throw new Error('indexes must be Uint16Array');
		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.index_buffer);
		gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indexes, gl.DYNAMIC_DRAW);
		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, null);
		this.index_count = indexes.length
	}

	set_colors(colors){
		if (!(colors instanceof Float32Array)) throw new Error('colors must be Float32Array');
		gl.bindBuffer(gl.ARRAY_BUFFER, this.color_buffer);
		gl.bufferData(gl.ARRAY_BUFFER, colors, gl.DYNAMIC_DRAW);
		gl.bindBuffer(gl.ARRAY_BUFFER, null);
	}

	/*set_normals(normals){
		if (!(normals instanceof Float32Array)) throw new Error('normals must be Float32Array');
		gl.bindBuffer(gl.ARRAY_BUFFER, this.normal_buffer);
		gl.bufferData(gl.ARRAY_BUFFER, normals, gl.DYNAMIC_DRAW);
		gl.bindBuffer(gl.ARRAY_BUFFER, null);
	}*/

	set(cpu_object){
		this.set_indexes(cpu_object.indexes)
		this.set_vertices(cpu_object.vertices)
		this.set_colors(cpu_object.colors)
		this.set_vao()
	}

	set_vao(){
		gl.bindVertexArray(this.vao);

		{
			gl.bindBuffer(gl.ARRAY_BUFFER, this.vertex_buffer);
			var coord = gl.getAttribLocation(shaderProgram, "coordinates");
			gl.vertexAttribPointer(coord, 3, gl.FLOAT, false, 0, 0);
			gl.enableVertexAttribArray(coord);

		}

		{
			gl.bindBuffer(gl.ARRAY_BUFFER, this.color_buffer);
			var colors = gl.getAttribLocation(shaderProgram, "colors");
			gl.vertexAttribPointer(colors, 4, gl.FLOAT, false, 0, 0); 
			gl.enableVertexAttribArray(colors);
		}

		//{
		//	gl.bindBuffer(gl.ARRAY_BUFFER, this.normal_buffer);
		//	var normals = gl.getAttribLocation(shaderProgram, "normals");
		//	gl.vertexAttribPointer(normals, 4, gl.FLOAT, false, 0, 0);
		//	gl.enableVertexAttribArray(normals);
		//}

		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.index_buffer);

		gl.bindVertexArray(null);
	}

	display() {
		gl.bindVertexArray(this.vao);
		gl.drawElements(gl.TRIANGLES, this.index_count, gl.UNSIGNED_SHORT, 0);
		gl.bindVertexArray(null);
	}
}


concatTypedArrays = (a, b) => { // a, b TypedArray of same type
	var c = new (a.constructor)(a.length + b.length);
	c.set(a, 0);
	c.set(b, a.length);
	return c;
}

class cpu_object{

	constructor() {
		this.vertices = new Vertices();
		this.indexes = new Uint16Array();
		this.colors = new Float32Array();
	}

	to_gpu_object(){
		o = new gpu_object()
		o.set_indexes(this.indexes);
		o.set_vertices(this.vertices);
		o.set_colors(this.colors);
		return o
	}

	add(cpu_object) {
		var L1 = this.vertices.length/3
		var ix2 = cpu_object.indexes.slice(0);
		for (var i = 0; i < ix2.length; ++i) ix2[i] += L1
		this.vertices = concatTypedArrays(new Float32Array(this.vertices), new Float32Array(cpu_object.vertices))
		this.indexes = concatTypedArrays(this.indexes, ix2)
		this.colors = concatTypedArrays(this.colors, cpu_object.colors)
	}

}


rayon_separe_parts_coeff = .05

/*make_pie_piece = (angle_min, angle_max, n, R, h, color) => {

	vs = new Vertices(2*n + 2);
	ix = new Uint16Array(3*4*(n-1) + 4*3);
	cs = new Float32Array(4*(2*n + 2));

	a_min = angle_min*2*Math.PI
	a_max = angle_max*2*Math.PI

	
	for (c = 0; c < n; ++c) {

		t = parseFloat(c)/parseFloat(n-1)
		
		a = a_min + t*(a_max-a_min)
		
		x = R*Math.cos(a)
		y = R*Math.sin(a)

		vs.set_p(2*c, x, y, .5*h)
		vs.set_p(2*c+1, x, y, -.5*h)

		j = 2*4*c
		cs[j + 0] = color[0]
		cs[j + 1] = color[1]
		cs[j + 2] = color[2]
		cs[j + 3] = color[3]

		cs[j + 4] = color[0]
		cs[j + 5] = color[1]
		cs[j + 6] = color[2]
		cs[j + 7] = color[3]

		if (c < n-1) {

			k = 3*4*c
			c_suiv = (c+1)%n

			// dessus
			ix[k + 0] = 2*n
			ix[k + 1] = 2*c
			ix[k + 2] = 2*c_suiv

			ix[k + 3] = 2*c
			ix[k + 4] = 2*c+1
			ix[k + 5] = 2*c_suiv

			ix[k + 6] = 2*c+1
			ix[k + 7] = 2*c_suiv
			ix[k + 8] = 2*c_suiv+1

			// dessous
			ix[k + 9] = 2*n+1
			ix[k + 10] = 2*c+1
			ix[k + 11] = 2*c_suiv+1
		}
	}

	vs.set_p(2*n, 0, 0, .5*h)
	vs.set_p(2*n+1, 0, 0, -.5*h)

	j = 2*4*n
	cs[j + 0] = color[0]
	cs[j + 1] = color[1]
	cs[j + 2] = color[2]
	cs[j + 3] = color[3]

	cs[j + 4] = color[0]
	cs[j + 5] = color[1]
	cs[j + 6] = color[2]
	cs[j + 7] = color[3]


	// limites
	k = 3*4*(n-1)
	ix[k + 0] = 2*n
	ix[k + 1] = 0
	ix[k + 2] = 1

	ix[k + 3] = 2*n
	ix[k + 4] = 2*n+1
	ix[k + 5] = 1

	ix[k + 6] = 2*n
	ix[k + 7] = 2*n-1
	ix[k + 8] = 2*n-2

	ix[k + 9] = 2*n
	ix[k + 10] = 2*n+1
	ix[k + 11] = 2*n-1

	for(var k = 0; k < vs.length; k+=3) {
		a = .5*(a_min+a_max)
		vs[k+0] += rayon_separe_parts_coeff*R*cos(a)
		vs[k+1] += rayon_separe_parts_coeff*R*sin(a)
	}


	o = new cpu_object()

	o.vertices = vs
	o.indexes = ix
	o.colors = cs

	return o
}*/


make_pie_piece = (angle_min, angle_max, n, r, R, h, color) => {

	vs = new Vertices(4*n);
	ix = new Uint16Array(3*8*(n-1) + 3*4);
	cs = new Float32Array(4*4*n);

	a_min = angle_min*2*Math.PI
	a_max = angle_max*2*Math.PI


	for(var j = 0; j < cs.length; j += 4) {
		cs[j + 0] = color[0]
		cs[j + 1] = color[1]
		cs[j + 2] = color[2]
		cs[j + 3] = color[3]
	}
	
	for (var i = 0; i < n; ++i) {

		const t = parseFloat(i)/parseFloat(n-1)
		
		const a = a_min + t*(a_max-a_min)
		
		const c = cos(a)
		const s = sin(a)

		const X = R*c
		const Y = R*s

		const x = r*c
		const y = r*s

		vs.set_p(4*i+0, x, y, -.5*h)
		vs.set_p(4*i+1, x, y, .5*h)
		vs.set_p(4*i+2, X, Y, .5*h)
		vs.set_p(4*i+3, X, Y, -.5*h)

		/*for(var j = 4*4*i; j < 4*4*(i+1); j += 4) {
			cs[j + 0] = color[0]
			cs[j + 1] = color[1]
			cs[j + 2] = color[2]
			cs[j + 3] = color[3]
		}*/

		if (i < n-1) {

			const k = 3*8*i
			const j = (i+1)%n


			for(var u = 0; u < 4; ++u) {
				// dessus
				ix[k + 0 + 6*u] = 4*i+u
				ix[k + 1 + 6*u] = 4*i+(1+u)%4
				ix[k + 2 + 6*u] = 4*j+u

				ix[k + 3 + 6*u] = 4*i+(1+u)%4
				ix[k + 4 + 6*u] = 4*j+u
				ix[k + 5 + 6*u] = 4*j+(1+u)%4

			}
		}
	}

	// limites
	k = 3*8*(n-1)
	ix[k + 0] = 0
	ix[k + 1] = 1
	ix[k + 2] = 2

	ix[k + 3] = 0
	ix[k + 4] = 2
	ix[k + 5] = 3

	ix[k + 6] = 4*(n-1)+0
	ix[k + 7] = 4*(n-1)+1
	ix[k + 8] = 4*(n-1)+2

	ix[k + 9] = 4*(n-1)+0
	ix[k + 10] = 4*(n-1)+2
	ix[k + 11] = 4*(n-1)+3

	for(var k = 0; k < vs.length; k+=3) {
		a = .5*(a_min+a_max)
		vs[k+0] += rayon_separe_parts_coeff*R*cos(a)
		vs[k+1] += rayon_separe_parts_coeff*R*sin(a)
	}


	o = new cpu_object()

	o.vertices = vs
	o.indexes = ix
	o.colors = cs

	return o
}



const make_bar = (x, y, z, dx, dy, dz, color) => {

    vs = new Vertices(8)
    cs = new Float32Array(4*8)
    ix = new Uint16Array([
        0,1,2,
        1,2,3,

        0,1,4,
        1,4,5,
        
        4,5,6,
        5,6,7,

        1,3,5,
        3,5,7,

        0,2,4,
        2,4,6,

        2,3,6,
        3,6,7
    ])

    for(c = 0; c < 8; ++c) {
        cs[4*c+0] = color[0]
        cs[4*c+1] = color[1]
        cs[4*c+2] = color[2]
        cs[4*c+3] = color[3]
    }

    vs.set_p(0, x, y, z)
    vs.set_p(1, x, y, z + dz)
    vs.set_p(2, x, y + dy, z)
    vs.set_p(3, x, y + dy, z + dz)
    vs.set_p(4, x + dx, y, z)
    vs.set_p(5, x + dx, y, z + dz)
    vs.set_p(6, x + dx, y + dy, z)
    vs.set_p(7, x + dx, y + dy, z + dz)

    o = new cpu_object()

    o.vertices = vs
    o.indexes = ix
    o.colors = cs

    return o
}


// background color
class background_color extends Float32Array {
	constructor(){ super([0,0,0,1]) }
	set(bg) {
		this[0] = bg[0]
		this[1] = bg[1]
		this[2] = bg[2]
		this[3] = bg[3]
		gl.clearColor(this[0], this[1], this[2], this[3])
	}
}

bg = new background_color()

gl.disable(gl.CULL_FACE)
gl.clearColor(bg[0], bg[1], bg[2], bg[3])
gl.enable(gl.DEPTH_TEST)
gl.enable(gl.BLEND)
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)


var P = null
var P_inv = null

//https://webglfundamentals.org/webgl/lessons/webgl-resizing-the-canvas.html
resizeCanvasToDisplaySize = (canvas) => {
	// Lookup the size the browser is displaying the canvas in CSS pixels.
	const displayWidth  = canvas.clientWidth * window.devicePixelRatio;
	const displayHeight = canvas.clientHeight * window.devicePixelRatio;
	// Check if the canvas is not the same size.
	const needResize = canvas.width  !== displayWidth ||
						canvas.height !== displayHeight;
	if (needResize) {
		// Make the canvas the same size
		canvas.width  = displayWidth;
		canvas.height = displayHeight;
	}
	return needResize;
}




class Base extends Float32Array{

	constructor(mat4x4 = null){
		super(
			mat4x4 === null ?
			[
				1, 0,   0,         0,
				0, 1,   0,         0,
				0, 0,   1,         0,
				0, 0,   0,         1
			]:
			mat4x4
		)
	}

	set_p(p) {
		this[12] = p[0]
		this[13] = p[1]
		this[14] = p[2]
	}

	get_p()  {
		return new Float32Array([this[12],this[13],this[14]])
	}


	set_rot(rot/* matrice de taille 3x3 */) {
		for(var l = 0; l < 3; ++l) {
			for(var c = 0; c < 3; ++c) {
				this[l+4*c] = rot[l+3*c]
			}
		}
	}

	set_my_rotation_to_my_rotation_mult_your_rotation(your_rotation) {
		var result_rotation = new Float32Array(3*3)
		for(var l = 0; l < 3; ++l) {
			for(var c = 0; c < 3; ++c){
				var sum = parseFloat(0)
				for(var k = 0; k < 3; ++k) {
					sum += this[l+4*k]*your_rotation[k+3*c]
				}
				result_rotation[l+3*c] = sum
			}
		}
		this.set_rot(result_rotation)
	}

	set_my_rotation_to_your_rotation_mult_my_rotation(your_rotation) {
		var result_rotation = new Float32Array(3*3)
		for(var l = 0; l < 3; ++l) {
			for(var c = 0; c < 3; ++c){
				var sum = parseFloat(0)
				for(var k = 0; k < 3; ++k) {
					sum += your_rotation[l+3*k]*this[k+4*c]
				}
				result_rotation[l+3*c] = sum
			}
		}
		this.set_rot(result_rotation)
	}

	rotate_around_the_x_axis(angle_radiants) {
		var c = cos(angle_radiants)
		var s = sin(angle_radiants)
		this.set_my_rotation_to_your_rotation_mult_my_rotation(
			new Float32Array([
				1, 0, 0,
				0, c, s,
				0, -s, c,
			])
		)
	}

	rotate_around_the_y_axis(angle_radiants) {
		var c = cos(angle_radiants)
		var s = sin(angle_radiants)
		this.set_my_rotation_to_your_rotation_mult_my_rotation(
			new Float32Array([
				c, 0, s,
				0, 1, 0,
				-s, 0, c,
			])
		)
	}

	get_invert() {
		var b = new Base()
		// inverser la rotation: transpose
		for(var l = 0; l < 3; ++l) {
			for(var c = 0; c < 3; ++c) {
				b[l+4*c] = this[c+4*l];
			}
		}
		// calculer la position: -rot_inv*p
		for(var l = 0; l < 3; ++l) {
			let sum = parseFloat(0)
			for(var k = 0; k < 3; ++k) {
				sum -= b[l+4*k]*this[k+4*3]
			}
			b[l+4*3] = sum
		}
		return b
	}

	get_image_pos(p) {
		var r = new Float32Array(3)
		for(var l = 0; l < 3; ++l) {
			let sum = this[l+4*3]
			for(var k = 0; k < 3; ++k) {
				sum += this[l+4*k]*p[k]
			}
			r[l] = sum
		}
		return r
	}

}



mult_mat4_vec4 = (mat4, vec4) => {
	var r = new Float32Array(4)
	for(var l = 0; l < 4; ++l) {
		let sum = parseFloat(0)
		for(var k = 0; k < 4; ++k) {
			sum += mat4[l+4*k]*vec4[k]
		}
		r[l] = sum
	}
	return r
}



translation = (d) => {
	return new Float32Array([
		1, 0, 0,  0,
		0, 1, 0,  0,
		0, 0, 1, 0,
		d[0], d[1], d[2], 1
	])
}

mult = (A, B) =>{
	R = new Float32Array([
		0, 0, 0, 0,
		0, 0, 0, 0,
		0, 0, 0, 0,
		0, 0, 0, 0
	])
	for(var l = 0; l < 4; ++l) {
		for(var c = 0; c < 4; ++c) {
			for(var k = 0; k < 4; ++k)
				R[l+4*c] += A[l+4*k]*B[k+4*c]
		}
	}
	return R
}



translate = (M, d) => {
	M[12] += d[0]
	M[13] += d[1]
	M[14] += d[2]

}
p = new Float32Array([0,0,0])

translated_copy = (M, d) => {
	R = new Float32Array(M)
	R[12] += d[0]
	R[13] += d[1]
	R[14] += d[2]
	return R
}




var vertShader = gl.createShader(gl.VERTEX_SHADER);
gl.shaderSource(vertShader,
'precision mediump float;\
attribute vec3 coordinates;\
attribute vec4 colors;\
uniform float t;\
uniform mat4 P, M;\
varying vec4 color;\
varying vec3 pm;\
void main(void) {\
	gl_Position = P*M*vec4(coordinates, 1.0);\
	pm = coordinates;\
	float a = cos(.5);\
	color = colors;\
}');
gl.compileShader(vertShader);

var fragShader = gl.createShader(gl.FRAGMENT_SHADER);
gl.shaderSource(fragShader,
'precision mediump float;\
varying vec4 color;\
varying vec3 pm;\
uniform float ombre;\
void main(void) {\
	/*float depth = gl_FragDepth;*/\
	gl_FragColor = color;\
	gl_FragColor.rgb += 2.*(2.*ombre - 1.)*(.5-.16*length(pm));\
}');
gl.compileShader(fragShader);


var shaderProgram = gl.createProgram();
gl.attachShader(shaderProgram, vertShader);
gl.attachShader(shaderProgram, fragShader);
gl.linkProgram(shaderProgram);

log_compilation_status = (shader) => {
	var compiled = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
	console.log('fragShader compiled successfully: ' + compiled);
	var compilationLog = gl.getShaderInfoLog(shader);
	console.log('Shader compiler log: ' + compilationLog);
}


log_compilation_status(fragShader)
log_compilation_status(vertShader)

gl.validateProgram(shaderProgram);
if (!gl.getProgramParameter(shaderProgram, gl.VALIDATE_STATUS)) {
	throw new Exception('validation failed')
}

var emplacement_t = gl.getUniformLocation(shaderProgram, "t");
var emplacement_P = gl.getUniformLocation(shaderProgram, "P");
var emplacement_M = gl.getUniformLocation(shaderProgram, "M");
var emplacement_ombre = gl.getUniformLocation(shaderProgram, "ombre");

total_quantity = parseFloat(0)
for (const e of input_data) total_quantity += e['quantity']
for (const e of input_data) e['ratio'] = e['quantity']/total_quantity


class Others_handler {

	constructor(slider_id = 'range_others_threshold') {
		this.original_input_data = undefined
		this.modified_input_data = undefined
		this._threshold = 0
		this.others = {
			name:'others',
			color: new Float32Array([Math.random(), Math.random(), Math.random(), 1])
		}

		const slider = document.getElementById(slider_id)
		slider.value = this._threshold
		const f = (e) => { this.threshold = Math.pow(slider.value, 4.6546) }
		slider.addEventListener("change", f)
		slider.addEventListener("input", f)
	}

	apply() {
		this.original_input_data = input_data
		this.modified_input_data = []

		this.others = {
			name: this.others.name,
			ratio: 0,
			quantity: 0,
			color: this.others.color
		}

		let count = 0

		//add_color_picker(others)

		for (const e of input_data) {
			if(e.ratio <= this._threshold) {
				count += 1
				this.others.ratio += e.ratio
				this.others.quantity += e.quantity
				//others.color[0] = ((count-1)*others.color[0] + e.color[0])/count
				//others.color[1] = ((count-1)*others.color[1] + e.color[1])/count
				//others.color[2] = ((count-1)*others.color[2] + e.color[2])/count
			}else{
				this.modified_input_data.push(e)
			}
		}

		this.modified_input_data.push(this.others)

		input_data = this.modified_input_data

		reset_color_pickers()
	}

	unapply() {
		input_data = (this.original_input_data ?? input_data)
	}

	set threshold(nval) {
		this._threshold = nval
		this.unapply()
		if(this._threshold > 0) {
			this.apply()
		}
		maj_pie()
		request_animation_frame()
	}

	get threshold() {
		return this._threshold
	}

	

}

const others_handler = new Others_handler()


let input_data_is_sorted = false
let non_sorted_input_data = null
let sorted_input_data = null

function switch_trier_input_data() {

	others_handler.unapply()

	non_sorted_input_data ??= input_data.slice() // clone
	sorted_input_data ??= input_data.slice() // clone

	

	input_data_is_sorted = !input_data_is_sorted

	if(input_data_is_sorted) {
		//console.log('sort')
		
		sorted_input_data.sort((a, b) => a.quantity - b.quantity)
		input_data = sorted_input_data
		//console.log(input_data)
	}
	else{
		//console.log('dont sort')
		input_data = non_sorted_input_data
	}

	others_handler.apply()
	maj_pie()
	request_animation_frame()
}





//pie = new cpu_object()


/*angle = 0// en tours

_count = 0
R = 4
for (var e of input_data) {
	
	ratio = e['ratio']

	new_piece = make_pie_piece(
		angle,
		_count == input_data.length-1 ? 1 : angle + ratio,// correct imprecisions for the last elm
		max(2, parseInt(ratio*100)),
		R,
		1,
		e['color']
	)

	e['color_index_range'] = [pie.colors.length/4, pie.colors.length/4 + new_piece.colors.length/4]

	pie.add(new_piece)
	my_angle = 2*PI*(angle + .5*ratio)
	R2 = 0.8*R
	e['pos'] = new Float32Array([R2*cos(my_angle),R2*sin(my_angle),0,1])

	

	angle += ratio
	++_count
	
}

pie = pie.to_gpu_object()*/

pie = new gpu_object()

rayon = 4
rayon_labels_coeff = 0.8
hauteur = 1
rayon_interne_ratio = .3



class Value{

	constructor(val) {
		this.val = val
	}

	set(val) {
		this.val = val
	}

	get() {
		return this.val
	}

}

class Barres_params{

	constructor() {
		this.dx = new Value(1)
		this.dy = new Value(1)
	}

}


barres_params = new Barres_params()

var display_type = 'pie'



const maj_pie = () => {

	var cpu = new cpu_object()

	angle = 0// en tours

	_count = 0
	
	for (var e of input_data) {
		
		ratio = e['ratio']

		new_piece = null

		if(display_type == 'pie') {

			const my_angle = 2*PI*(angle + .5*ratio)

			new_piece = make_pie_piece(
				angle,
				_count == input_data.length-1 ? 1 : angle + ratio,// correct imprecisions for the last elm
				max(2, parseInt(ratio*90)),
				rayon_interne_ratio*rayon,
				rayon,
				hauteur,
				e['color']
			)

			e['pos'] = new Float32Array([
				rayon_labels_coeff*rayon*cos(my_angle),
				rayon_labels_coeff*rayon*sin(my_angle),
				0,
				1
			])
		}
		else if (display_type == 'horizontal bars' || display_type == 'vertical bars') {

			// hauteur -> epaisseur
			// rayon -> largeur

			var d_long = rayon/4
			var d_profond = rayon_interne_ratio/.3

			const x = parseFloat(_count-.5*input_data.length)*(4*rayon_separe_parts_coeff+d_long) - .5*d_long
			const y = -.5*d_profond
			max_ratio = 0.001
			for (var u of input_data) {
				max_ratio = parseFloat(max(max_ratio, u['ratio']))
			}

			const H_coeff = 13*hauteur

			const H = H_coeff*max_ratio

			if(display_type == 'horizontal bars') {

				new_piece = make_bar(
				
					-.5*H,
					x,
					y,
					
					ratio*H_coeff,
					
					d_long,
					d_profond,
					e['color']
				)
	
				e['pos'] = new Float32Array([
					
					(1.9*rayon_labels_coeff/2.5-.7)*H,
					x+.5*d_long,
					y,
					1
				])
			}
			else if(display_type == 'vertical bars') {

				new_piece = make_bar(
				
					x,
					-.5*H,
					
					y,
					
					
					
					d_long,
					
					ratio*H_coeff,
					d_profond,
					
					

					e['color']
				)
	
				e['pos'] = new Float32Array([
					x+.5*d_long,
					
					(1.9*rayon_labels_coeff/2.5-.7)*H,
					y,
					
					1
				])

			}
			
		}

		e['color_index_range'] = [cpu.colors.length/4, cpu.colors.length/4 + new_piece.colors.length/4]

		cpu.add(new_piece)
		
		
		

		

		angle += ratio
		++_count
		
	}
	
	pie.set(cpu)
}

maj_pie()

const switch_to_vertical_bars = () => {
	log('switch_to_bars')
	display_type = 'vertical bars'
	document.getElementById('nom_range_rayon').innerText = 'largeur'
	document.getElementById('nom_range_rayon_interne_ratio').innerText = 'profondeur'
	document.getElementById('nom_range_rayon_labels').innerText = 'position labels'
	maj_pie()
	request_animation_frame()
}

const switch_to_horizontal_bars = () => {
	log('switch_to_bars')
	display_type = 'horizontal bars'
	document.getElementById('nom_range_rayon').innerText = 'largeur'
	document.getElementById('nom_range_rayon_interne_ratio').innerText = 'profondeur'
	document.getElementById('nom_range_rayon_labels').innerText = 'rayon labels'
	maj_pie()
	request_animation_frame()

}

const switch_to_pie = () => {
	log('switch_to_pie')
	display_type = 'pie'
	document.getElementById('nom_range_rayon').innerText = 'rayon'
	document.getElementById('nom_range_rayon_interne_ratio').innerText = 'rayon_interne'
	document.getElementById('nom_range_rayon_labels').innerText = 'rayon labels'
	maj_pie()
	request_animation_frame()
}

const maj_bars = ()=>{



}



M = new Base()

//var pressedKeys = {90:false, 83:false, 81:false, 68:false, 67:false, 88:false};
var pressedKeys = {90:false, 83:false, 81:false, 68:false, 67:false, 88:false};
window.onkeyup = function(e) {
	if(e.keyCode in pressedKeys) {
		pressedKeys[e.keyCode] = false
	}
}
window.onkeydown = function(e) {
	log('keydown', e.keyCode)
	if(e.keyCode in pressedKeys) {
		pressedKeys[e.keyCode] = true
		request_animation_frame()
	}
}

range_separate_pieces = document.getElementById('range_separate_pieces')
range_separate_pieces.value = rayon_separe_parts_coeff
{
	var f = (e)=>{
		rayon_separe_parts_coeff = range_separate_pieces.value
		maj_pie()
		request_animation_frame()
	}
	range_separate_pieces.addEventListener("change", f)
	range_separate_pieces.addEventListener("input", f)
}


range_rayon = document.getElementById('range_rayon')
range_rayon.value = rayon/parseFloat(2*4)
{
	var f = (e)=>{
		rayon = 2*4*range_rayon.value
		maj_pie()
		request_animation_frame()
	}
	range_rayon.addEventListener("change", f)
	range_rayon.addEventListener("input", f)
}


range_hauteur = document.getElementById('range_hauteur')
range_hauteur.value = hauteur/parseFloat(5)
{
	var f = (e)=>{
		hauteur = 5*range_hauteur.value
		maj_pie()
		request_animation_frame()
	}
	range_hauteur.addEventListener("change", f)
	range_hauteur.addEventListener("input", f)
}

input_color_bg = document.getElementById('color_bg')
input_color_bg.value = rgbToHex(255*bg[0], 255*bg[1], 255*bg[2])
{
	var f = (e)=>{
		var c = hexToRgb(input_color_bg.value)
		bg.set([
			c[0]/255,
			c[1]/255,
			c[2]/255,
			1
		])
		request_animation_frame()
	}
	input_color_bg.addEventListener("change", f)
	input_color_bg.addEventListener("input", f)
}

input_range_bg_alpha = document.getElementById('range_bg_alpha')
input_range_bg_alpha.value = bg[3]
{
	var f = (e)=>{
		var alpha = input_range_bg_alpha.value
		bg.set([
			bg[0],
			bg[1],
			bg[2],
			alpha
		])
		request_animation_frame()
	}
	input_range_bg_alpha.addEventListener("change", f)
	input_range_bg_alpha.addEventListener("input", f)
}




range_rayon_interne_ratio = document.getElementById('range_rayon_interne_ratio')
range_rayon_interne_ratio.value = rayon_interne_ratio
{
	var f = (e)=>{
		rayon_interne_ratio = range_rayon_interne_ratio.value
		maj_pie()
		request_animation_frame()
	}
	range_rayon_interne_ratio.addEventListener("change", f)
	range_rayon_interne_ratio.addEventListener("input", f)
}


range_rayon_labels = document.getElementById('range_rayon_labels')
range_rayon_labels.value = rayon_labels_coeff/2.5
{
	var f = (e)=>{
		rayon_labels_coeff = 2.5*range_rayon_labels.value
		maj_pie()
		request_animation_frame()
	}
	range_rayon_labels.addEventListener("change", f)
	range_rayon_labels.addEventListener("input", f)
}


const range_ombre = document.getElementById('range_ombre')
range_ombre.value = .7
{
	function f(e) { request_animation_frame() }
	range_ombre.addEventListener("change", f)
	range_ombre.addEventListener("input", f)
}




class slider_value {

	constructor(id, initial_val = .5, mod = (val) => val) {
		this.elm = document.getElementById(id)
		this.elm.value = initial_val
		this.mod = mod
		var f = (e)=> {
			maj_pie()
			request_animation_frame()
		}
		this.elm.addEventListener("change", f)
		this.elm.addEventListener("input", f)
	}

	get val() {
		return this.mod(this.elm.value)
	}
}

taille_labels = new slider_value('range_taille_labels', .5, val => 2*val)





voir_pourcentages = true
checkbox_voir_pourcentages = document.getElementById('checkbox_voir_pourcentages')
checkbox_voir_pourcentages.checked = voir_pourcentages
switch_voir_pourcentages = () => {
	checkbox_voir_pourcentages.checked = voir_pourcentages = !voir_pourcentages
	maj_pie()
	request_animation_frame()
}

voir_qté = false
checkbox_voir_qté = document.getElementById('checkbox_voir_qté')
checkbox_voir_qté.checked = voir_qté
switch_voir_qté = () => {
	checkbox_voir_qté.checked = voir_qté = !voir_qté
	maj_pie()
	request_animation_frame()
}


class Hold_clic{
	constructor(){
		this.dx = 0
		this.dy = 0
		this.on_mouse_move = (e) => {
			this.dx = e.movementX * window.devicePixelRatio
			this.dy = e.movementY * window.devicePixelRatio
			request_animation_frame();
		}
		this.lors = false
		superposition.addEventListener('mousedown', (e) => { this.deb() });
		window.addEventListener('mouseup', (e) => { this.fin() });
		window.addEventListener('blur', (e) => { this.fin() });

	}
	deb(){
		if(this.lors) return
		this.lors = true
		window.addEventListener('mousemove', this.on_mouse_move);
	}
	fin(){
		if(!this.lors) return
		this.lors = false
		this.dx = 0
		this.dy = 0
		window.removeEventListener('mousemove', this.on_mouse_move)
	}
}

hold_clic = new Hold_clic()

p[2] = -9

//document.querySelectorAll("*").forEach(element => element.addEventListener("scroll", ({target}) => console.log(target, target.id, target.parent, target.parent.id)));

/*document.body.addEventListener('scroll', () => {
	log('scroll '+window.scrollX+' '+window.scrollY)
	lastKnownScrollPosition = window.scrollY;
	p[2] += window.scrollY;
	p[0] += window.scrollX;
});*/


var label = document.createElement('label');
label.innerHTML = "something";    
canvas.appendChild(label);


dx = 0
dy = 0


window.addEventListener('blur', (event) => {
	//log("UNFOCUS", pressedKeys)
	for(key in pressedKeys) pressedKeys[key] = false
	//log("after", pressedKeys)
});




time_prev = parseFloat(0)

// firefox ne supporte pas roundRect
//https://stackoverflow.com/questions/1255512/how-to-draw-a-rounded-rectangle-using-html-canvas
draw_2d_rounded_rect = (
	x,
	y,
	width,
	height,
	radius = 5,
	fill = false,
	stroke = true
) => {
	if (typeof radius === 'number') {
		radius = {tl: radius, tr: radius, br: radius, bl: radius};
	} else {
		radius = {...{tl: 0, tr: 0, br: 0, bl: 0}, ...radius};
	}
	ctx_2d.beginPath();
	ctx_2d.moveTo(x + radius.tl, y);
	ctx_2d.lineTo(x + width - radius.tr, y);
	ctx_2d.quadraticCurveTo(x + width, y, x + width, y + radius.tr);
	ctx_2d.lineTo(x + width, y + height - radius.br);
	ctx_2d.quadraticCurveTo(x + width, y + height, x + width - radius.br, y + height);
	ctx_2d.lineTo(x + radius.bl, y + height);
	ctx_2d.quadraticCurveTo(x, y + height, x, y + height - radius.bl);
	ctx_2d.lineTo(x, y + radius.tl);
	ctx_2d.quadraticCurveTo(x, y, x + radius.tl, y);
	ctx_2d.closePath();
	if (fill) ctx_2d.fill();
	if (stroke) ctx_2d.stroke();
}






update_color_buffer = (input) => {
	const color = input['color']
	//log('color', color)
	const [i, j] = input['color_index_range']
	var colors = new Float32Array(4*(j - i))
	for(var k = 0; k < j-i; ++k) {
		colors[4*k+0] = color[0]
		colors[4*k+1] = color[1]
		colors[4*k+2] = color[2]
		colors[4*k+3] = color[3]
	}
	//log('colors', colors)
	gl.bindBuffer(gl.ARRAY_BUFFER, pie.color_buffer);
	//gl.bufferSubData(gl.ARRAY_BUFFER, i*4*4, colors, 0, 2*(j-i));
	//gl.bufferSubData(gl.ARRAY_BUFFER, i*4, colors, 4*(j-i));
	gl.bufferSubData(gl.ARRAY_BUFFER, i*4*Float32Array.BYTES_PER_ELEMENT, colors, 0, colors.length);
	//gl.bindBuffer(gl.ARRAY_BUFFER, null)
	request_animation_frame()
}

//color_inputs = []

let color_pickers = []

function add_color_picker(e) {
	var color_picker = document.createElement('input')
	//elem2.innerHTML = "something"
	color = e['color']
	color_picker.type = 'color'
	//elm.value = 'rgba('+255*color[0]+','+255*color[1]+','+255*color[2]+','+color[3]+')'
	color_picker.value = rgbToHex(round(255*color[0]), round(255*color[1]), round(255*color[2]))

	var f = (ev)=>{
		const selectedColor = ev.currentTarget.value
		//log(selectedColor)
		const new_color = hexToRgb(selectedColor)
		var color = e['color']
		color[0] = parseFloat(new_color[0])/255
		color[1] = parseFloat(new_color[1])/255
		color[2] = parseFloat(new_color[2])/255
		color[3] = parseFloat(1)
		update_color_buffer(e)
	}

	color_picker.addEventListener('change', f, false);
	color_picker.addEventListener('input', f, false);

	document.getElementById('superposition').append(color_picker)
	//color_inputs.push(color_picker)
	e['color_picker'] = color_picker

	color_pickers.push(color_picker)
}


function reset_color_pickers() {

	for(let e of color_pickers) { e.remove() }

	color_pickers = []

	for(let e of input_data) { add_color_picker(e) }
}


reset_color_pickers()






animate = (time) => {
	
	dt = 4*(time - time_prev)

	a_key_is_pressed = false
	
	/*if(pressedKeys[90]) p[2] -= .0005*dt
	if(pressedKeys[83]) p[2] += .0005*dt

	if(pressedKeys[68]) p[0] += .0005*dt
	if(pressedKeys[81]) p[0] -= .0005*dt

	if(pressedKeys[67]) p[1] += .0005*dt
	if(pressedKeys[88]) p[1] -= .0005*dt*/


	a_key_is_pressed =
		pressedKeys[90] || pressedKeys[83]
		|| pressedKeys[68] || pressedKeys[81]
		|| pressedKeys[67] || pressedKeys[88]

	M.set_p(p)

	if(hold_clic.dx) dx = hold_clic.dx
	else dx *= exp(-.001*dt)
	if(hold_clic.dy) dy = hold_clic.dy
	else dy *= exp(-.001*dt)
	if (projection_type == '3D') {
		M.rotate_around_the_x_axis(.006*dy)
		M.rotate_around_the_y_axis(-.006*dx)
	}
	
	hold_clic.dy = 0
	hold_clic.dx = 0

	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

	gl.useProgram(shaderProgram);
	gl.uniform1f(emplacement_t, time);
	gl.uniformMatrix4fv(emplacement_P, false, P);
	gl.uniformMatrix4fv(emplacement_M, false, M);
	gl.uniform1f(emplacement_ombre, range_ombre.value);

	pie.display()

	time_prev = time

	let PM = mult(P, M)

	let p1_abs = new Float32Array([4,0,0])

	let p1 = mult_mat4_vec4(PM, new Float32Array([p1_abs[0], p1_abs[1], p1_abs[2], 1]))

	x = canvas_2d.width * .5* (p1[0]/p1[2] + 1)
	y = canvas_2d.height * (1 - .5 * (p1[1]/p1[2] + 1))


	ctx_2d.clearRect(0, 0, canvas_2d.width, canvas_2d.height);

	char_h = taille_labels.val*min(20, .06*min(canvas_2d.width, canvas_2d.height))

	ctx_2d.font = char_h + "px arial"
	ctx_2d.lineWidth = 1
	//ctx_2d.fillStyle = ctx_2d.strokeStyle = "rgba(.1,.1,.1,.9)"
	ctx_2d.textAlign = "center"
	ctx_2d.textBaseline = "middle"

	if(see_lables) {
		for (const e of input_data) {
			let pe = mult_mat4_vec4(PM, e['pos'])
			x = canvas_2d.width * .5* (pe[0]/pe[2] + 1)
			y = canvas_2d.height * (1 - .5 * (pe[1]/pe[2] + 1))

			//log('label.x =', x)
			//log('label.y =', y)
			
			color = e['color']
			name = e['name']
			//qté = e['quantity'].toFixed(2)
			qté = Math.round(e['quantity'] * 100) / 100
			percent = (100*e['ratio']).toFixed(0)+'%'

			ctx_2d.textBaseline = 'middle';
			ctx_2d.textAlign = 'center';

			padding = 0.3*char_h
			hr = char_h
			if(voir_pourcentages) hr += char_h
			if(voir_qté) hr += char_h
			hr += padding

			wr = ctx_2d.measureText(name).width
			if(voir_pourcentages) wr = max(wr, ctx_2d.measureText(percent).width)
			if(voir_qté) wr = max(wr, ctx_2d.measureText(qté).width)
			wr += padding
			//ctx_2d.fillStyle = ctx_2d.strokeStyle = 'rgba('+color[0].toFixed(0)+','+color[1].toFixed(0)+','+color[2].toFixed(0)+','+color[3].toFixed(0)+')'
			//ctx_2d.fillStyle = ctx_2d.strokeStyle = 'red'
			//color_txt = 'rgba('+color[0].toFixed(2)+','+color[1].toFixed(2)+','+color[2].toFixed(2)+','+color[3].toFixed(2)+')'
			//log('rgba('+color[0].toFixed(2)+','+color[1].toFixed(2)+','+color[2].toFixed(2)+','+color[3].toFixed(2)+')')
			//log(color_txt)
			//ctx_2d.fillStyle = ctx_2d.strokeStyle = 'red'
			//ctx_2d.fillStyle = ctx_2d.strokeStyle = color
			//ctx.globalAlpha = 0.2;
			//ctx_2d.fillStyle = ctx_2d.strokeStyle = 'rgba('+color[0]*255+','+color[1]*255+','+color[2]*255+','+color[3]+')'
			//ctx_2d.rect(x - .5*wr, y - .5*hr, wr, hr);
			//ctx_2d.fillRect(x - .5*wr, y - .5*hr, wr, hr);
			//ctx_2d.fillStyle = 'rgba('+color[0].toFixed(0)+','+color[1].toFixed(0)+','+color[2].toFixed(0)+','+color[3].toFixed(0)+')';
			//ctx_2d.fill();

			ctx_2d.save()

			is_dark = (color[0] + color[1] + color[2] < .5)

			//ctx_2d.beginPath()
			
			//ctx_2d.roundRect(x - .5*1.05*wr, y - .5*1.05*hr, 1.05*wr, 1.05*hr,[.5*char_h])
			
			
			// norme rgb
			Lc = sqrt(color[0]**2 + color[1]**2 + color[2]**2)
			// couleur normalisé
			cn = Lc > .0001 ? new Float32Array([color[0]/Lc, color[1]/Lc, color[2]/Lc]) : new Float32Array([0.577350, 0.577350, 0.577350])
			// decalage couleur
			coef_border = is_dark ? .2 : -.2
			//ctx_2d.fillStyle = 'rgba('+(color[0]+coef_border*cn[0])*255+','+(color[1]+coef_border*cn[1])*255+','+(color[2]+coef_border*cn[2])*255+','+color[3]+')'
			ctx_2d.strokeStyle = 'rgba('+(color[0]+coef_border*cn[0])*255+','+(color[1]+coef_border*cn[1])*255+','+(color[2]+coef_border*cn[2])*255+','+color[3]+')'
			eps = .05
			ctx_2d.lineWidth = min(max(eps*wr, eps*hr), 3.)
			//draw_2d_rounded_rect(x - .5*(1+eps)*wr, y - .5*(1+eps)*hr, (1+eps)*wr, (1+eps)*hr, .5*char_h, false, true)
			draw_2d_rounded_rect(x - .5*wr, y - .5*hr, wr, hr, .5*char_h, false, true)
			
			//ctx_2d.fill()

			//ctx_2d.beginPath()
			//ctx_2d.roundRect(x - .5*wr, y - .5*hr, wr, hr,[10])
			//draw_2d_rounded_rect(x - .5*wr, y - .5*hr, wr, hr, 10)
			//ctx_2d.fillStyle = 'rgba('+color[0]*255+','+color[1]*255+','+color[2]*255+','+color[3]+')'
			ctx_2d.fillStyle = 'rgba('+color[0]*255+','+color[1]*255+','+color[2]*255+','+color[3]+')'
			//ctx_2d.fill()
			draw_2d_rounded_rect(x - .5*wr, y - .5*hr, wr, hr, .5*char_h, true, false)
			ctx_2d.restore()

			

			if(is_dark){
				ctx_2d.fillStyle = ctx_2d.strokeStyle = "rgba(245,254,245,.9)"
			}else{
				ctx_2d.fillStyle = ctx_2d.strokeStyle = "rgba(1,1,1,.9)"
			}

			var txt_dy = char_h
			var txt_nb_lines = 1 + voir_pourcentages + voir_qté
			//var txt_y = y - .25*char_h - .5*(txt_nb_lines-1)*txt_dy
			var txt_y = y + .25*char_h - .5*(txt_nb_lines-1)*txt_dy
			
			
			//ctx_2d.fillText(name, x, y-(voir_pourcentages ? .25*char_h : -.25*char_h ))
			ctx_2d.fillText(name, x, txt_y)
			txt_y += txt_dy
			if(voir_pourcentages) {
				ctx_2d.fillText(percent, x, txt_y)
				txt_y += txt_dy
			}
			if(voir_qté) ctx_2d.fillText(qté, x, txt_y)

			color_picker = e['color_picker']

			//color_picker.style.left = '600px';
			//color_picker.style.left = round(x) + 'px';
			//color_picker.style="position:absolute;left:"+round(x-.5*wr)+"px;top:"+round(y-.5*hr)+"px;width:"+round(wr)+"px;height:"+round(hr)+"px;opacity:0;"
			color_picker.style=`position:absolute;left:${round(x-.5*wr)}px;top:${round(y-.5*hr)}px;width:${round(wr)}px;height:${round(hr)}px;opacity:0;`
			
			//ctx_2d.fillText(e['quantity'], x, y+char_h);

			
		}
	} else {// see_labels == false
		for (const e of input_data) {
			//e.color_picker.style.display = 'none'
			e.color_picker.style.visibility = 'hidden'
			e.color_picker.style.pointerEvents = 'none'
		}
	}

	animationFrameRequested = false

	if(a_key_is_pressed || abs(dx) >= .01 && abs(dy) >= .01) {
		request_animation_frame();
	}

	/*if(!done) {
		//https://stackoverflow.com/questions/10673122/how-to-save-canvas-as-an-image-with-canvas-todataurl

		// here is the most important part because if you dont replace you will get a DOM 18 exception.
		var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");

		// it will save locally
		window.location.href = image;

	}*/

	if(save_image_after_next_render) {

		save_image_after_next_render = false

		//superposition
		//superposition = document.getElementById('superposition')

		var png_canvas = document.createElement('canvas')

		png_canvas.clientWidth = canvas.clientWidth
		png_canvas.clientWidth = canvas.clientHeight
		png_canvas.width = canvas.width
		png_canvas.height = canvas.height
		

		//grab the context from your destination canvas
		var png_ctx_2d = png_canvas.getContext('2d');
		
		//call its drawImage() function passing it the source canvas directly
		png_ctx_2d.drawImage(canvas, 0, 0);
		if(see_lables) png_ctx_2d.drawImage(canvas_2d, 0, 0);


		// here is the most important part because if you dont replace you will get a DOM 18 exception.
		//var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream")
		//var image = superposition.toDataURL("image/png").replace("image/png", "image/octet-stream")
		var image = png_canvas.toDataURL("image/png").replace("image/png", "image/octet-stream")

		function download_image(image, name = 'image.png') {
			const a = document.createElement('a')
			a.href = image
			a.download = name
			document.body.appendChild(a)
			a.click()
			document.body.removeChild(a)
		}

		download_image(image)
		// it will save locally
		//window.location.href = image
		//window.location.download = 'image.png'
		//downloadImage(dataURL, 'image.png')
	}
		
}

done = false



animationFrameRequested = false

request_animation_frame = () => {
	if(!animationFrameRequested) {
		animationFrameRequested = true
		window.requestAnimationFrame(animate);
	}
}


see_lables = true

switch_see_labels = () => {
	see_lables = !see_lables
	document.getElementById('checkbox_see_labels').checked = see_lables
	request_animation_frame()
}


save_image_after_next_render = false
save_image = () => {
	//https://stackoverflow.com/questions/10673122/how-to-save-canvas-as-an-image-with-canvas-todataurl
	save_image_after_next_render = true
	request_animation_frame()
}


randomise_colors = () => {
	for(var e of input_data) {
		e['color'] = new Float32Array([Math.random(),Math.random(),Math.random(),1])
		update_color_buffer(e)
	}
	request_animation_frame()
}


var projection_type = '3D'

const switch_projection_matrix = () => {
	if (projection_type == '2D') {
		//gl.depthFunc(gl.LESS)
		projection_type = '3D'
	}else {
		//gl.depthFunc(gl.GREATER)
		dx = 0
		dy = 0
		M.set_rot([1,0,0, 0,1,0, 0,0,1])
		projection_type = '2D'
	}
	update_wh()
}


update_wh = () => {
	resizeCanvasToDisplaySize(gl.canvas);
	resizeCanvasToDisplaySize(canvas_2d);
	w = gl.canvas.width
	h = gl.canvas.height
	aspect = parseFloat(w)/parseFloat(h)
	fov = Math.PI/3
	a = parseFloat(1)/Math.tan(fov/2)
	far = parseFloat(1000)
	near = parseFloat(.1)

	if (projection_type == '3D') {
		P = new Float32Array([
			a/aspect,	0,			0,							0,
			0,			a,			0,							0,
			0,			0,			-(near+far)/(far-near),		-1,
			0,			0,			-2*far*near/(far-near),		0
		])
		/*P_inv = new Float32Array([
			aspect/a,	0,					0,				0,
			0,			parseFloat(1)/a,	0,				0,
			0,			0,					0,				(near-far)/(2*far*near),
			0,			0,					-1,				(near+far)/(2*far*near),
		])*/
	}
	else {
		
		const h1 = 2*Math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)*Math.tan(fov/2)
		//const h1 = w1



		/*P = new Float32Array([
			2/h1/aspect,		0,					0,							0,
			0,					2/h1,				0,							0,
			0,					0,					-1.0/(far-near),			0,
			0,					0,					-near/(far-near),			1
		])*/

		/*P = new Float32Array([
			-2/h1/aspect,		0,					0,							0,
			0,					-2/h1,				0,							0,
			0,					0,					1.0/(far-near),				0,
			0,					0,					1,							1
		])*/

		/*P = new Float32Array([
			2/h1/aspect,		0,					0,							0,
			0,					2/h1,				0,							0,
			0,					0,					-1.0/(far-near),				0,
			0,					0,					-1,							1
		])*/

		P = new Float32Array([
			2/h1/aspect,		0,					0,							0,
			0,					2/h1,				0,							0,
			0,					0,					1.0/(far-near),				0,
			0,					0,					1,							1
		])

	}
	
	
	resizeCanvasToDisplaySize(gl.canvas);
	gl.viewport(0, 0, w, h);

	request_animation_frame();
}
update_wh()
window.addEventListener("resize", ()=>{update_wh()}, true);


request_animation_frame();
//animate(0);
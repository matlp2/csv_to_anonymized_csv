
'''
exemple de creation de table :

colum_names = ['c1', 'c2']
rows = [
	[42, 'hi'],
	[587, 'there'],
	[777, 'bingo']
]

with Html() as my_html:

	with block('html'):


		with block('head'):

			html += f'<script src="sortable-master/js/sortable.modifié.js"></script>'

		with block('body'):

			with block('style', type = '"text/css"'):
				html += """
table.table-full-width {
	width:100%;
	padding: 0px;
	spacing: 0px;
	border-spacing: 0px;
}
tr:nth-of-type(odd) {
	background-color:rgb(235, 235, 235);
}
tr.tr-colum-names {
	background-color:rgb(205, 105, 105);
}"""

			with block('table', 'class = "table-full-width"'):

				with block('thead'):
					with block('tr'):
						for column_name in colum_names:
							with block('th', 'data-sorted="false"', one_liner = True):
								html.s += column_name
				
				with block('tbody'):
					for row in rows:
						with block('tr'):
							for cell in row:
								with block('td', one_liner = True):
									html.s += str(cell)
									
	print(my_html)
	my_html.save('test_my_html.html')

produit

<html >
        <head >
                <script src="sortable-master/js/sortable.modifié.js"></script>
        </head>
        <body >
                <style >

                        table.table-full-width {
                                width:100%;
                                padding: 0px;
                                spacing: 0px;
                                border-spacing: 0px;
                        }
                        tr:nth-of-type(odd) {
                                background-color:rgb(235, 235, 235);
                        }
                        tr.tr-colum-names {
                                background-color:rgb(205, 105, 105);
                        }
                </style>
                <table class = "table-full-width">
                        <thead >
                                <tr >
                                        <th data-sorted="false">c1</th>
                                        <th data-sorted="false">c2</th>
                                </tr>
                        </thead>
                        <tbody >
                                <tr >
                                        <td >42</td>
                                        <td >hi</td>
                                </tr>
                                <tr >
                                        <td >587</td>
                                        <td >there</td>
                                </tr>
                                <tr >
                                        <td >777</td>
                                        <td >bingo</td>
                                </tr>
                        </tbody>
                </table>
        </body>
</html>


'''


class Html:

	def __init__(self):
		self.s = ''
		self.newline = '\n'

	def __iadd__(self, s):
		s = str(s)
		s = s.replace('\n', self.newline)
		self.s += self.newline + s
		return self

	def __repr__(self):
		return self.s;

	def __str__(self):
		return self.s;

	def indent(self):
		self.newline += '\t'

	def unindent(self):
		if(len(self.newline) > 1):
			self.newline = self.newline[:-1]

	def save(self, filename):
		with open(filename, 'w+') as file:
			file.write(self.s)

	#exemple d'utilisation de enter/exit :
	#html_table = Html()
	#with html_table:
	#	with block('table'):
	#		...

	def __enter__(self):
		global html
		self._previous_html = html
		html = self
		return self

	def __exit__(self, type, value, traceback):
		global html
		html = self._previous_html
		self._previous_html = None
		# don't return self, otherwise raised exceptions will be ignored



html = Html()# html décriture par défault


class block:

	def __init__(self, name, params='', **kw):
		self.name = name
		self.is_a_one_liner = kw.get('one_liner', False)
		global html
		self.html = kw.get('html', html)# global html by default
		self.params = params

	def __enter__(self):
		self.html += f'<{self.name} {self.params}>'
		if not self.is_a_one_liner:
			self.html.indent()
		return self

	def __exit__(self, type, value, traceback):
		if self.is_a_one_liner:
			self.html.s += f'</{self.name}>'
		else:
			self.html.unindent()
			self.html += f'</{self.name}>'
		# don't return self, otherwise raised exceptions will be ignored
	










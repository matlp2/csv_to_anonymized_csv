
from termcolor import colored, cprint

class prt:

	pile = []

	def __init__(self, *args, **kwargs):
		self.color = kwargs.get('color', None)
		self.block_end = kwargs.get('block_end', None)
		self.block_decoration = kwargs.get('block_decoration', {'start':'{','end':'}\n'})
		self._prt(*args, **{key:val for key,val in kwargs.items() if key != 'color' and key != 'block_end' and key != 'block_decoration0'})
		
		
	def _prt(self, *args, **kwargs):
		print(*(colored(len(prt.pile)*'\t' + str(a), *((self.color,) if self.color else ()) ) for a in args), **kwargs)

	def __enter__(self):
		self._prt(self.block_decoration['start'])
		prt.pile.append(self)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		prt.pile.pop()
		self._prt(self.block_decoration['end'], end = self.block_end if self.block_end != None else '\n')
		
		#if self.block_end != None:
			#self._prt(self.block_end)

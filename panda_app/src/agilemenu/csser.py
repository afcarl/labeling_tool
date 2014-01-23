# Copyright (c) 2012, Joseph Bumstead
# All rights reserved.
# See included "SimplifiedBSDLicense.txt"


from clevercss import Engine, ParserError, EvalException
import re

base = """
	// This kind of comment works in clevercss...
	//    /* But this kind will NOT work. */
menu:
	font: Tuffy_Bold.ttf
	font-size: 1.5
	padding: .2, .5, .05, -.1111
	margin: 0, 0, 0, 0
	bevel: .35
	color: #c0c0c0
	border-Color: #c0c0c0
	background-Color: #707070
	shadow-offset: 0.03, 0.03
	shadow-color: 0,0,0,1
	slant: 0.3
	border-thickness: 2
	separator: 
		height: .5
		thick: 2
"""

	
pppp = re.compile(r'- *\.')
def negInsertZero(cssText): #/* NOTE: negatives need a digit befor the dot! */
	return pppp.sub(r'-0.', cssText)

def hex2PandaColor(h):
	return float(int(h[1:3], 16))/256, float(int(h[3:5], 16))/256, float(int(h[5:7], 16))/256, 1.0

def cssDictionary(cssText):
	di = {}
	for selectors, defs in Engine(negInsertZero(cssText)).evaluate():
		#print selectors, defs 
		de = {}
		for d in defs: #isnumeric():
			if d[1][0].isalpha(): de[d[0]] =  d[1]
			else:
				dd = d[1].split(',')
				if len(dd)>1:
					ddd = [float(n) for n in dd]
					for i in range(len(ddd)):
						if ddd[i] > 100: ddd[i]=100-ddd[i]
					de[d[0]] = tuple(ddd)
				else:
					v = dd[0]
					if v[0] == '#':
						de[d[0]] = hex2PandaColor(v)
					else: de[d[0]] = float(v)
		for s in selectors:
			if s in di: # allready in dictionary
				# add def or redefine: 
				for e in de: di[s][e] = de[e]
			else: di[s] = de.copy() # need copy here so redefines will be independent.
	#for s in di: print s, di[s]
	return di


def getStyle(selectors, sheet=None):
	css = getCSS(sheet)
	style = {}
	for se in selectors:
		s = se.split()
		ss = ''
		while len(s):
			ss += s.pop(0)
			if ss in css:
				for i in css[ss]:
					style[i] = css[ss][i]
			ss += ' '
			#if '.threatLevel2' in selectors: print ss,style
	#if '.threatLevel2' in selectors: print css
	return style

cssMemoi = {'base.ccss': cssDictionary(base)}
def getCSS(fn=None):
	if fn in cssMemoi: return cssMemoi[fn]
	if fn == None: return cssMemoi['base.ccss']
	try:
		with open(fn) as f:
			cssMemoi[fn]= cssMemoi['base.ccss'].copy()
			cssMemoi[fn].update(cssDictionary(f.read()))
			f.close()
		return cssMemoi[fn]
	except IOError as e:
		print 'css file not found: using base ccss.'
		return cssMemoi['base.ccss']

def main():
	di = getCSS()
	for i in di: print i, di[i]

if __name__ == '__main__':
    main()

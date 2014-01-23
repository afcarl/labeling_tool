# Copyright (c) 2012, Joseph Bumstead
# See included "SimplifiedBSDLicense.txt"

from panda3d.core import PandaNode, NodePath
from pandac.PandaModules import PGItem
from buttonjoe import MenuItem, DORMANT, READY, splitOn, newID
import re

delimiter='>>'

def stripComments(lines):
	commentPrefix = ''
	if '=' in lines[0]:
		firstL = lines[0].split('=')
		if firstL[0] == 'commentPrefix':
			commentPrefix = firstL[1].split()[0]
			lines.pop(0)
			prefixLen = len(commentPrefix)
			outL =[]
			for l in lines:
				if l.lstrip()[0:prefixLen]!=commentPrefix:
					outL.append(l.split(commentPrefix)[0])
			return outL
	return lines

def count(t):
	c=0
	for i in t:
		if type(i)==list: c+=countd(i)
		elif type(i)==dict:
			c+=1
			if 'children' in i: c += count(i['children'])
	return c

def indent2tree2(lines, R=[], ndnt=0):
	if len(lines)>0:
		line=lines[0].lstrip()
		nxndnt= len(lines[0])-len(line) # the number of tabs
		if nxndnt == ndnt:
			R.append({'itmTxt':line})
			return indent2tree2(lines[1:], R, ndnt)
		if nxndnt > ndnt:
			children=indent2tree2(lines, [], nxndnt)
			R[len(R)-1]['children']=children #parent is right-most list item
			return indent2tree2(lines[count(children):], R, ndnt)# skip past children
	return R # if no more lines or unindent recursion


def fixMultiLines(inL):
	""" In the menu source txt, a menu item with line-breaks
		is indicated as consecutive lines without delimiter,
		with the last line having a delimiter.
		This function joins these lines into a single outline entry.
	"""
	outLines=[]
	multiLine=''
	ndnt=0
	leastNdnt = 99999
	for l in inL:
		line=l.lstrip()
		if delimiter not in line:
			ndnt= len(l)-len(line) # the number of tabs
			leastNdnt = min(leastNdnt, ndnt)
			nndnt = max(0,ndnt-leastNdnt)
			multiLine+=nndnt*' '+line.rstrip()+'\n'# append with cr.
		elif len(multiLine):        # last line of multLine (has delimiter)
			multiLine+=nndnt*' '+line.rstrip()# append last multiline.
			outLines.append(leastNdnt*' '+multiLine) # re-indent and accumulate to outLines
			multiLine=''
			ndnt=0
			leastNdnt = 99999
		else:
			outLines.append(l)       # regular line
	return outLines


def menuItemParse(strng, isParent):
	"""
	strng can be:
			"menuText" : makes a parent item if there are children, otherwise an 'info' item.
			"menuText|| kind=button, someClickFunction(arg,.. argn)" : makes a button with a click action.
			"menuText|| kind=checkBox, someClickFunction(arg,.. argn)" : makes a checkBox with a click action.
			"menuText|| kind=radioBTN, someClickFunction(arg,.. argn), groupID=radioBTNGroupID" :
				A  radioBTN that interacts with radioBTNs that have the same groupID .
			"menuText|| kind=<whatever>" : makes an item without a click action.
	Given strng = "menuText|| kind=kind, clickFunction(arg,.. argn), class=val1 val2 valn, key=val, key=val,..."
	where
			menuText is what shows in the menu,
			'delimiter' and what follows are options to guide the menu item response:
				* kind can be one of {'parent', 'button', 'checkBox', 'radioBTN', etc.}
				* clickFunction is the name of the function to call,
				* and arg(s) are the variable names of arguments for the function.
				* Use any key=value(s) to suit your app (separate multiple values with spaces, no commas except after last)
				* for radio buttons, use key,val groupID=<grpId> to identify their group,
				* for css id selector use key,val id=<uniqueID> (used by styler and your menu modification code)
				* for css class selectors use key,val class=className1 className2 ... (remember: spaces, no commas except after last)
	"""
	p =splitOn(strng, delimiter)# txt, rest
	r = {'txt': p[0], 'kind':'info', 'id': newID(), 'args':None}
	if len(p)>1: # if not just txt
			leftnright=p[1]
			if '\n' in leftnright: # the odd multiLine case with function etc attached
				t = leftnright.split('\n',1)
				r['txt']+= '\n'+t[1]    # append rest of multiLines
				leftnright=t[0]         # extract the kind, function, args.

			if len(leftnright) > 1:
				leftnFargs = leftnright.split('(')
				left = splitOn(leftnFargs[0], ',')
				right = []
				if len(leftnFargs) > 1:
					fargsnright = splitOn(leftnFargs[1], ')')
					if len(fargsnright)>0:
						if fargsnright[0][0]==',':
								right = splitOn(fargsnright[0], ',')
						else: r['args'] = fargsnright[0]
					if len(fargsnright) > 1:
						right = splitOn(fargsnright[1], ',')
					r['func'] = left[-1]               # get the func
					left = left[:-1] #minus the func
				leftnright = left+right       # concat
			if leftnright > 0:
				for p in leftnright:
					kw, val = splitOn(p, '=')
					r[kw] = val
	if isParent: r['kind']='parent'
	elif r['txt'][:3] == '---': r['kind']='separator'
	return r

def indent2tree(data):
	global delimiter
	lines=[s for s in data.split('\n') if s.strip()]# list of non blank lines
	lines=stripComments(lines)
	delimiter = lines.pop(0).split('=')[1].strip()
	lines=fixMultiLines(lines)
	outL=indent2tree2(lines,[])
	return outL

def getWidest(grp):
	widest=0
	for i in grp.getChildren(): # get widest child
		widest = max(widest, i.getPythonTag('extras').getFWidth())
	return widest

def verticalGroupFinish(grp, test=False):
	grpN = NodePath(grp)
	widest = getWidest(grpN) # get prelim size
	vertPos=0
	for i in grpN.getChildren(): # finish siblings
		c = i.node().getPythonTag('extras')
		#if not test:
                c.finish(pos=(0,0,-vertPos), minWidth=widest)
		vertPos+=c.getFHeight()# finished height
	widest = getWidest(grpN) # get finished size
	for i in grpN.getChildren(): # finish siblings
		cnp = NodePath(i).find('-PandaNode')
		if cnp: cnp.setX(widest)
	grpN.hide()

def horizontalGroupFinish(grp):
	xPos=0
	for i in NodePath(grp).getChildren(): # finish siblings
		c = i.node().getPythonTag('extras')
		kids = NodePath(c).find('-PandaNode')
		if kids:
			kids.setPos(0,0,-c.getFHeight()-c.getFMargin()[2])
		c.finish(pos=(xPos,0,0))
		xPos += c.getFWidth()


class Menu():
	def __init__(self,
			context,
			outline,
			menuRootID=None,
			title='',
			closeAction='_',
			scale=.07,
			pos=(-.8,0,.8),
			parent=aspect2d,
			style = None,
			tipe = 'vertical'):
		self.context = context
		if menuRootID == None: self.menuRootID = newID()
		else: self.menuRootID = menuRootID
		self.scale=scale
		self.style=style
		t = indent2tree(outline)
		if tipe=='titleBar':
			t=[{'itmTxt':title+delimiter, 'children':t[:]}, {'itmTxt':'X'+delimiter+' kind=close, closeAction='+closeAction}]
		root = self.makeMenu('root', t, PandaNode('ehh'), tipe)
		self.np=parent.attachNewNode(root)
		self.np.setScale(scale)
		firstItemPath = self.np.find('-PGItem')
		f= firstItemPath.node().getPythonTag('extras').getFFrame()
		self.np.setPos(pos[0],pos[0],pos[2]-f[3]*scale)
		self.showing=False
		self.menu_Click=False
		self.clickBlock=False
		self.showIt()

	def makeItem(self, item, tipe = 'vertical'):
		if 'children' in item:
			mItem = menuItemParse(item['itmTxt'], isParent=True)
			if tipe in ('horizontal', 'titleBar'):  mItem['kind'] = tipe
			mi=MenuItem(self, mItem, self.style)
			self.makeMenu(mItem['txt'], item['children'], parent=mi)
		else:
			mItem = menuItemParse(item['itmTxt'], isParent=False)
			mi=MenuItem(self, mItem, self.style)
		return mi

	def makeMenu(self, name, t, parent, tipe = 'vertical'):
		sybGroup=PandaNode(name)
		parent.addChild(sybGroup)
		for item in t:# make menu syblings
			mi = self.makeItem(item, tipe)
			sybGroup.addChild(mi)
		if tipe=='vertical': verticalGroupFinish(sybGroup)
		elif tipe=='horizontal':
			horizontalGroupFinish(sybGroup)
		elif tipe=='titleBar': horizontalGroupFinish(sybGroup)
		return sybGroup

	def addItems(self, items, nextToID, after=True):
		nextToPath = self.np.find('**/=id='+nextToID)
		sybGroup = NodePath(nextToPath.node().getParent(0))
		menuItms = self.makeMenu('tmp', indent2tree(items), sybGroup.node())
		sybs = sybGroup.getChildren()
		sybGroup.node().removeAllChildren()
		for s in sybs:
			if s.node().hasPythonTag('extras'):
				s.node().getPythonTag('extras').deformat()
				if s == nextToPath:
					if after:
						s.reparentTo(sybGroup)
						for m in NodePath(menuItms).getChildren():
							m.getPythonTag('extras').deformat()
							m.reparentTo(sybGroup)
					else:
						for c in NodePath(menuItms).getChildren():
							c.getPythonTag('extras').deformat()
							c.reparentTo(sybGroup)
						s.reparentTo(sybGroup)
				else: sybGroup.node().addChild(s.node())
		verticalGroupFinish(sybGroup.node())

	def delete(self, delID):
		delPath = self.np.find('**/=id='+delID)
		height = 0
		sybGroup = delPath.node().getParent(0)
		sybs = NodePath(sybGroup).getChildren()
		n=0
		ndx=0
		for s in sybs:
			if s == delPath:
				xtrs = delPath.getPythonTag('extras')
				height = xtrs.getFHeight()
				xtrs.abandon()
				sybGroup.removeChild(delPath.node())
				ndx = n
			else: s.setZ(s.getZ()+height)
			n+=1
		return sybGroup.getParent(0), ndx
		
	def replace(self, id, withItem):
		parnt, ndx = self.delete(id)
		self.addchildren_(withItem, NodePath(parnt), insertPoint=ndx)

	def replaceChild(self, parentID, ndx, withItem):
		self.deleteChild(parentID, ndx)
		self.addchildren(withItem, parentID, insertPoint=ndx)

	def deleteChild(self, parentID, nChild):
		parPath = self.np.find('**/=id='+parentID)
		height = 0
		sybGroup = parPath.find('-PandaNode')
		sybs = sybGroup.getChildren()
		n=0
		for s in sybs:
			if n==nChild:
				xtrs = s.getPythonTag('extras')
				height = xtrs.getFHeight()
				xtrs.abandon()
				sybGroup.node().removeChild(s.node())
			else: s.setZ(s.getZ()+height)
			n+=1

	def addchildren(self, items, parentID, insertPoint=-1):
		parent = self.np.find('**/=id='+parentID)
		self.addchildren_(items, parent, insertPoint)

	def addchildren_(self, items, parent, insertPoint):
		menuItms = self.makeMenu('tmp', indent2tree(items), PandaNode('tmp'))
		sybGroup = parent.find('-PandaNode')
		sybs=[]
		if sybGroup.isEmpty():
			sybGroup=parent.attachNewNode(parent.getName())
			sybGroup.setX(parent.node().getPythonTag('extras').getFWidth())
		else:
			sybs = sybGroup.getChildren()
			sybGroup.node().removeAllChildren()
		n, inserted = 0, False
		for s in sybs:
                        #print "@@hi"
			if n == insertPoint:
				for m in NodePath(menuItms).getChildren():
					m.getPythonTag('extras').deformat()
					m.reparentTo(sybGroup)
				#print "@@inserted"
				inserted=True
			s.getPythonTag('extras').deformat()
			s.reparentTo(sybGroup)
			n+=1
		if not inserted: #insertPoint was beyond last child...
                        #print "@@not hi"
			for m in NodePath(menuItms).getChildren():
				m.getPythonTag('extras').deformat()
				m.reparentTo(sybGroup)
		verticalGroupFinish(sybGroup, True)
		sybGroup.hide()

	def setReady(self, id):
		self.np.find('**/=id='+id).node().setState(READY)

	def setDormant(self, id):
		self.np.find('**/=id='+id).node().setState(DORMANT)

	def leftClickSim(self, id):
		messenger.send('press'+id, ['simClk'])

	def setPos(self, pos=(0,0,0)):
		self.np.setPos(pos)

	def isOpen(self):
		return self.showing
		
	def showIt(self):
		self.np.show()
		self.showing = True
	def hideIt(self):
		self.np.hide()
		# Give mouse listener a chance to consume events:
		self.showing=False
		self.menuClick_()


	def menuClicked(self):
		return self.menu_Click or self.clickBlock

	def menuClick_(self):
		self.menu_Click = True
		taskMgr.doMethodLater(.3, self.ackHideIt, 'ackHider', [])
	def ackHideIt(self):
		self.menu_Click=False
	

class HorizontalMenu(Menu):
	def __init__(self,
			context,
			outline,
			scale=.07,
			style = None):
		Menu.__init__(self,
			context = context,
			outline=outline,
			scale=scale,
			style=style,
			tipe = 'horizontal')

class DraggableMenu(Menu):
	def __init__(self,
			context,
			outline,
			title='',
			closeAction='hide',
			scale=.07,
			style = None):
		Menu.__init__(self,
			context = context,
			outline=outline,
			title=title,
			closeAction=closeAction,
			scale=scale,
			style=style,
			tipe = 'titleBar')

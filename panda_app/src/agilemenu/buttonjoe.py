# Copyright (c) 2012, Joseph Bumstead
# See included "SimplifiedBSDLicense.txt"

import inspect, math
from pandac.PandaModules import PGItem, PGFrameStyle, MouseButton, PandaNode, NodePath, LineSegs, CardMaker
from panda3d.core import TextNode
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from csser import getCSS, getStyle


def splitOn(strng, ch):
	return [s.strip() for s in strng.split(ch) if s.strip()]

def getSpaceGap(gap, font=None):
	txtn = TextNode('tt')
	if font: txtn.setFont(font)
	s = ''
	txtn.setText(s)
	while txtn.getWidth() < gap:
			s += ' '
			txtn.setText(s)
	return s

iidd=0
def newID():
	global iidd
	iidd+=1
	return 'KrAzY'+str(iidd)

def rect(ls, frame):
	ls.moveTo(frame[1],0,frame[2])
	ls.drawTo(frame[1],0,frame[3])
	ls.drawTo(frame[0],0,frame[3])
	ls.drawTo(frame[0],0,frame[2])
	ls.drawTo(frame[1],0,frame[2])

def diamond(ls, frame):
	hh = frame[2]+(frame[3]-frame[2])/2
	hw = frame[0]+(frame[1]-frame[0])/2
	ls.moveTo(frame[0],0,hh)
	ls.drawTo(hw,0,frame[3])
	ls.drawTo(frame[1],0,hh)
	ls.drawTo(hw,0,frame[2])
	ls.drawTo(frame[0],0,hh)

def cross(ls, frame):
	hh = frame[2]+(frame[3]-frame[2])/2
	hw = frame[0]+(frame[1]-frame[0])/2
	ls.moveTo(frame[0]+.08,0,hh)
	ls.drawTo(frame[1]-.08,0,hh)
	ls.moveTo(hw,0,frame[2]+.08)
	ls.drawTo(hw,0,frame[3]-.08)

def ex(ls, frame):
	ls.moveTo(frame[0],0,frame[2])
	ls.drawTo(frame[1],0,frame[3])
	ls.moveTo(frame[0],0,frame[3])
	ls.drawTo(frame[1],0,frame[2])

def bevelBox(ls, frame, bevel):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls.moveTo(frame[0]+bevel,0,frame[3])
	ls.drawTo(frame[1]-bevel,0,frame[3])
	ls.drawTo(frame[1],0,frame[3]-bevel)
	ls.drawTo(frame[1],0,frame[2]+bevel)
	ls.drawTo(frame[1]-bevel,0,frame[2])
	ls.drawTo(frame[0]+bevel,0,frame[2])
	ls.drawTo(frame[0],0,frame[2]+bevel)
	ls.drawTo(frame[0],0,frame[3]-bevel)
	ls.drawTo(frame[0]+bevel,0,frame[3])

def fill(filler, frame, BGColor, lineThick, bevel = None, arrowhead = None):
	h = frame[3]-frame[2]
	incr = 10/float(base.win.getProperties().getYSize())
	bg = LineSegs()
	bg.setColor(BGColor)
	bg.setThickness(lineThick)
	for i in range(1,int(h*33)):
		if bevel and arrowhead:
			filler(bg, [frame[0]+incr*i,frame[1]-incr*i,frame[2]+incr*i,frame[3]-incr*i], bevel, arrowhead)
		elif bevel:
			filler(bg, [frame[0]+incr*i,frame[1]-incr*i,frame[2]+incr*i,frame[3]-incr*i], bevel)
		elif arrowhead:
			filler(bg, [frame[0]+incr*i,frame[1]-incr*i,frame[2]+incr*i,frame[3]-incr*i], arrowhead)
		else:
			filler(bg, [frame[0]+incr*i,frame[1]-incr*i,frame[2]+incr*i,frame[3]-incr*i])
	fnp = NodePath(bg.create())
	fnp.setBin("fixed", 10) 
	return fnp

def bevelBG(frame, bevel=.35, lineThick=2, color=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls = LineSegs()
	ls.setThickness(lineThick)
	if color != 'transparent':
		ls.setColor(color)
		bevelBox(ls, frame, bevel)
	else:
		ls.setColor(1,1,1,1)
		# ls.moveTo(0,0,0)
		# ls.drawTo(0,0,1)
	a = ls.create()
	if BGColor:
		fill(bevelBox, frame, BGColor, lineThick, bevel).reparentTo(NodePath(a))
	return a

def checkBox(frame, bevel=.35, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls = LineSegs('off')
	ls.setThickness(lineThick)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		bevelBox(ls, frame, bevel)
	else:
		ls.setColor(color)
	hoff = min(2*bevel, h/4)
	rect(ls, (frame[0]+hoff,frame[0]+hoff+h/2,frame[2]+h/4,frame[3]-h/4))
	a = ls.create()
	if BGColor:
		fill(bevelBox, frame, BGColor, lineThick, bevel).reparentTo(NodePath(a))
	return a

def xBox(frame, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	bx = LineSegs('xbox')
	rect(bx, (frame[1]-h/4,frame[1]-3*h/4,frame[2]+h/4,frame[3]-h/4))
	ex(bx, (frame[1]-h/4,frame[1]-3*h/4,frame[2]+h/4,frame[3]-h/4))
	box = bx.create()
	if BGColor:
		fill(rectangleLine, frame, BGColor, lineThick).reparentTo(NodePath(box))
	return box

def checkedBox(frame, bevel=.35, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls = LineSegs('on')
	ls.setThickness(lineThick)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		bevelBox(ls, frame, bevel)
	else:
		ls.setColor(color)
	rect(ls, (frame[0]+h/4,frame[0]+3*h/4,frame[2]+h/4,frame[3]-h/4))
	ex(ls, (frame[0]+h/4,frame[0]+3*h/4,frame[2]+h/4,frame[3]-h/4))
	a = ls.create()
	if BGColor:
		fill(bevelBox, frame, BGColor, lineThick, bevel).reparentTo(NodePath(a))
	return a

def radioBTN(frame, bevel=.35, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls = LineSegs('off')
	ls.setThickness(lineThick)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		bevelBox(ls, frame, bevel)
	else:
		ls.setColor(color)
	diamond(ls, (frame[0]+h/4,frame[0]+3*h/4,frame[2]+h/4,frame[3]-h/4))
	a = ls.create()
	if BGColor:
		fill(bevelBox, frame, BGColor, lineThick, bevel).reparentTo(NodePath(a))
	return a

def checkedRadioBTN(frame, bevel=.35, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	w = frame[1]-frame[0]
	h = frame[3]-frame[2]
	ls = LineSegs('on')
	ls.setThickness(lineThick)
	f=(frame[0]+h/4,frame[0]+3*h/4,frame[2]+h/4,frame[3]-h/4)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		bevelBox(ls, frame, bevel)
	else:
		ls.setColor(color)
	diamond(ls, f)
	cross(ls, f)
	a = ls.create()
	if BGColor:
		fill(bevelBox, frame, BGColor, lineThick, bevel).reparentTo(NodePath(a))
	return a

def bevelArrowLine(ls, frame, bevel, arrowhead):
	ls.moveTo(frame[0]+bevel,0,frame[3])
	ls.drawTo(frame[1]-bevel,0,frame[3])
	ls.drawTo(frame[1]-bevel+arrowhead,0, frame[2]+(frame[3]-frame[2])/2)
	ls.drawTo(frame[1]-bevel,0,frame[2])
	ls.drawTo(frame[0]+bevel,0,frame[2])
	ls.drawTo(frame[0],0,frame[2]+bevel)
	ls.drawTo(frame[0],0,frame[3]-bevel)
	ls.drawTo(frame[0]+bevel,0,frame[3])

def bevelArrow(frame, bevel=.35, arrowhead=.4, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	ls = LineSegs()
	ls.setThickness(lineThick)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		bevelArrowLine(ls, frame, bevel, arrowhead)
	else:
		ls.setColor(color)
	a = ls.create()
	if BGColor:
		fill(bevelArrowLine, frame, BGColor, lineThick, bevel, arrowhead).reparentTo(NodePath(a))
	return a

def rectangleLine(ls, frame):
	ls.moveTo(frame[1],0,frame[2])
	ls.drawTo(frame[1],0,frame[3])
	ls.drawTo(frame[0],0,frame[3])
	ls.drawTo(frame[0],0,frame[2])
	ls.drawTo(frame[1],0,frame[2])

def rectangle(frame, lineThick=2, color=(1,1,1,1), brdrColor=(1,1,1,1), BGColor = None):
	ls = LineSegs()
	ls.setThickness(lineThick)
	if brdrColor != 'transparent':
		ls.setColor(brdrColor)
		rectangleLine(ls, frame)
	else:
		ls.setColor(color)
	a = ls.create()
	if BGColor:
		fill(rectangleLine, frame, BGColor, lineThick).reparentTo(NodePath(a))
	return a

# def arrow(frame, arrowhead=.4, color=(1,1,1,1), lineThick=2):
	# ls = LineSegs()
	# ls.setColor(color)
	# ls.setThickness(lineThick)
	# ls.moveTo(frame[0],0,frame[2])
	# ls.drawTo(frame[1],0,frame[2])
	# ls.drawTo(frame[1]+arrowhead,0, frame[2]+(frame[3]-frame[2])/2)
	# ls.drawTo(frame[1],0,frame[3])
	# ls.drawTo(frame[0],0,frame[3])
	# ls.drawTo(frame[0],0,frame[2])
	# return ls.create()

def sepLine(frame, styles):
	style = styles['menu separator']
	ls = LineSegs('sepLine')
	ls.setColor(style['color'])
	ls.setThickness(style['thick'])
	hpad = (frame[1]-frame[0])*.2
	hh = frame[3]+(frame[3]-frame[2])#/2
	ls.moveTo(frame[0]+hpad,0,hh)
	ls.drawTo(frame[1]-hpad,0,hh)
	return ls.create()

def loadSound(itm, event, style, selector):
	try:
		v = selector+'-volume'
		if v in style: vol = style[v]
		else: vol = .5
		if itm.item['kind'] == 'titleBar':
			itm.dragSound = base.loader.loadSfx(style[selector])
			itm.dragSound.setVolume(vol)
			r = selector+'-rate'
			if r in style: itm.dragRate = style[r]
			else: itm.dragRate = 111
		else:
			sound = base.loader.loadSfx(style[selector])
			sound.setVolume(vol)
			itm.setSound(event, sound)
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)


READY=0
HOVER=1
SUBDUED=2
CLICK=3
DORMANT=4
stateName = ['ready','hover','subdued','click','dormant']
STATES = range(READY, DORMANT+1)

checkBoxShim = '   '
def getBackgroundSet(menuItem, frame, arrowhead):
	item = menuItem.item
	kind = item['kind']
	txt = item['txt']
	grphcs = []
	slctrs = ['menu '+kind]
	if 'class' in item: # class after kind: class has higher priority
		slctrs.append('.'+item['class'])
	if 'id' in item: # id after class: id has higher priority
		slctrs.append('#'+item['id'])
	style = getStyle(slctrs, menuItem.cssFName)
	if 'enter-sound' in style: loadSound(menuItem, menuItem.getEnterEvent(), style, 'enter-sound')
	if 'exit-sound' in style: loadSound(menuItem, menuItem.getExitEvent(), style, 'exit-sound')
	if 'press-sound' in style: loadSound(menuItem, menuItem.getPressEvent(MouseButton.one()), style, 'press-sound')
	if 'release-sound' in style: loadSound(menuItem, menuItem.getReleaseEvent(MouseButton.one()), style, 'release-sound')
	if 'drag-sound' in style: loadSound(menuItem, None, style, 'drag-sound')
	for state in STATES:
		slctrs = ['menu '+kind+' :'+stateName[state].lower()]
		if 'class' in item: # class after kind: class has higher priority
			slctrs.append('.'+item['class']+' :'+stateName[state].lower())
		if 'id' in item: # id after class: id has higher priority
			slctrs.append('#'+item['id']+' :'+stateName[state].lower())
		style = getStyle(slctrs, menuItem.cssFName)
		# Want to add more style properties?
		# Do it here:
		# Match style keys here to property names in .ccss
		fontSize = style['font-size']
		bevel = style['bevel']*fontSize
		font  = style['font']
		color = style['color']
		tn = TextNode(txt)
		tn.setText(txt)
		tn.setFont(loader.loadFont(font))
		tn.setSlant(style['slant'])
		tn.setTextColor(color)
		tn.setShadow(*style['shadow-offset'])
		tn.setShadowColor(*style['shadow-color'])
		NodePath(tn).setScale(fontSize)
		sHolder = NodePath(PandaNode('sHolder'))
		sHolder.attachNewNode(tn)
		grphcs.append(sHolder)
		sHolder.attachNewNode(tn)
		borderColor = style['border-Color']
		thk = style['border-thickness']
		if 'background-Color' in style and\
			style['background-Color'] != 'transparent':
			bgColor = style['background-Color']
		else: bgColor = None
		if kind=='parent':
			if state==HOVER: ar = arrowhead*2
			else: ar = arrowhead
			grphcs[state].attachNewNode(bevelArrow(frame, bevel, ar, thk, color, borderColor, bgColor))
		elif kind in ('horizontal', 'titleBar', 'close'):
			grphcs[state].attachNewNode(rectangle(frame, thk, color, borderColor, bgColor))
		elif kind=='checkBox':
			grphcs[state].attachNewNode(checkBox(frame, bevel, thk, color, borderColor, bgColor))
			cb = grphcs[state].attachNewNode(checkedBox(frame, bevel, thk, color, borderColor, bgColor))
			cb.hide()
		elif kind=='radioBTN':
			grphcs[state].attachNewNode(radioBTN(frame, bevel, thk, color, borderColor, bgColor))
			cb = grphcs[state].attachNewNode(checkedRadioBTN(frame, bevel, thk, color, borderColor, bgColor))
			cb.hide()
		else:
			grphcs[state].attachNewNode(bevelBG(frame, bevel, thk, borderColor, bgColor))
	return grphcs

def onEnter(menuRootID, itm, pos):
	taskMgr.remove(menuRootID+'leaver') # preempt possible pending onLeave()'s
	me = itm.getPythonTag("extras")
	me.menuRoot.clickBlock = True
	sibList=itm.getParent(0)
	for x in range(sibList.getNumChildren()):# hide sibling's kids
			bro = sibList.getChild(x)
			NodePath(bro).setBin("fixed", 11) 
			kind = bro.getPythonTag("extras").item['kind']
			if kind in ('parent', 'vertical', 'horizontal', 'titleBar', 'close') and bro.getNumChildren()>0:
				NodePath(bro.getChild(0)).hide()
			if bro.getState()!=DORMANT: bro.setState(SUBDUED)
	if itm.getState()!=DORMANT:
			itm.setState(HOVER)
			NodePath(itm).setBin("fixed", 50) 
			if itm.getNumChildren(): # show children
				cdrn=itm.getChild(0)
				np = NodePath(cdrn)
				np.show()
				for x in range(cdrn.getNumChildren()): #show HOVERed's children
						c=cdrn.getChild(x)
						ckind = c.getPythonTag("extras").item['kind']
						if ckind =='parent': # but not their children
							NodePath(c.getChild(0)).hide()
						if c.getState()!=DORMANT: c.setState(READY)    
	while sibList.getName() != 'root': #Hilite ancestors
			p=sibList.getParent(0)
			NodePath(p).show()
			p.setState(HOVER)    
			sibList=p.getParent(0)

def onLeave(menuRootID, itm, pos):
	"""
	When we leave a menu item, we want to hide its children.
	But what if we're entering a child?
	Let's scedule the hiding for fraction of second later
	to give onEnter(child) a chance to preempt the hiding with taskMgr.remove('leaver')
	"""
	try:
		me = itm.getPythonTag("extras")
		me.menuRoot.clickBlock = False
		taskMgr.doMethodLater(.5, onLeave2, menuRootID+'leaver', [.25, menuRootID,itm])
	except:
		pass

def onLeave2(t, mrID, itm):
	"""
	Assume that we've left the menu entirely: shut it down to the root.
	Let onEnter preempt this in case we left this item to enter another.
	"""
	if itm.getNumChildren():
			NodePath(itm.getChild(0)).hide()   
	if itm.getState()!=DORMANT: itm.setState(READY)
	try:
		if itm.getParent(0).getName() != 'root':
			taskMgr.doMethodLater(t, onLeave2, mrID+'leaver', [t/2, mrID, itm.getParent(0).getParent(0)])
		else:
			for x in range(itm.getParent(0).getNumChildren()):
				c=itm.getParent(0).getChild(x)
				if c.getState()!=DORMANT: c.setState(READY)
	except: pass

def toggle(itm):
	tog = itm.getTag('toggle')
	if tog=='on':
			tog='off'
			for state in STATES:
				s = itm.getStateDef(state)
				s.find('**/on').hide()
				s.find('**/off').show()
	else:
			tog='on'
			for state in STATES:
				s = itm.getStateDef(state)
				s.find('**/off').hide()
				s.find('**/on').show()
	itm.setTag('toggle', tog)
	return tog=='on'

def checkAll(itm, grpID):
	os=NodePath(itm.getParent(0)).findAllMatches('**/=groupID='+grpID)
	for o in os: # check'm
		if o.getTag('toggle')=='off': messenger.send('press'+o.getTag('id'), ['simClk'])

def unCheckAll(itm, grpID):
	os=NodePath(itm.getParent(0)).findAllMatches('**/=groupID='+grpID)
	for o in os: # check'm
		if o.getTag('toggle')=='on': messenger.send('press'+o.getTag('id'), ['simClk'])

def radioToggle(itm, grpID):
	os=NodePath(itm.getParent(0)).findAllMatches('**/=groupID='+grpID)
	for o in os: # uncheck peers
			o.setTag('toggle', 'off')
			for state in STATES:
				oo=o.node().getStateDef(state)
				oh = oo.find('**/on')
				if oh: oh.hide()
				oh = oo.find('**/off')
				if oh: oh.show()
	for state in STATES: # check self
			s = itm.getStateDef(state)
			s.find('**/off').hide()
			s.find('**/on').show()
	itm.setTag('toggle', 'on')
	
def closeMenu(itm, pos):
	it = itm.getPythonTag("extras")
	# print it.item['txt'], it.item['closeAction']
	if it.item['closeAction']=='abandon':
		it.abandon()
		os=NodePath(itm.getParent(0))
		os.remove_node()
	elif it.item['closeAction']=='hide':
		it.menuRoot.hideIt()

def printf(t):
	print 'onPress ', t ,'function not found.'

def dragger(menu, me, xOff, yOff):
	if base.mouseWatcherNode.hasMouse():
		x=base.mouseWatcherNode.getMouseX()*base.getAspectRatio()
		y=base.mouseWatcherNode.getMouseY()
		menu.setPos(x+xOff,0,y+yOff)
		if me.lastX == None:
			me.lastX=x+1
			me.lastY=y+1
		dragRate = math.sqrt((me.lastX-x)*(me.lastX-x)+(me.lastY-y)*(me.lastY-y))*me.dragRate
		me.lastX=x
		me.lastY=y
		#print int(dragRate)
		me.dragSound.setPlayRate(dragRate)
	return Task.cont

def onPress(itm, pos):
	me = itm.getPythonTag("extras")
	me.menuRoot.menuClick_()
	item = me.item
	kind = item['kind']
	txt = item['txt'].strip()
	groupID = itm.getTag('groupID')
	if 'id' in item: id=item['id']
	else: id=''
	selfPac = {'txt':txt, 'id':id, 'groupID':groupID, 'kind':kind}
	if itm.getState()!=DORMANT:
		itm.setState(CLICK)
		if kind =='checkBox': selfPac['checked']=toggle(itm)
		elif kind =='radioBTN': radioToggle(itm, groupID)
		elif kind =='checkAllBTN': checkAll(itm, groupID)
		elif kind =='unCheckAllBTN': unCheckAll(itm, groupID)
		elif kind =='close': closeMenu(itm, pos)
		elif kind =='titleBar':
			if base.mouseWatcherNode.hasMouse():
				menu = me.menuRoot.np
				xOff=menu.getX()-base.mouseWatcherNode.getMouseX()*base.getAspectRatio()
				yOff=menu.getZ()-base.mouseWatcherNode.getMouseY()
				me.lastX = None
				me.lastY = None
				taskMgr.add(dragger, 'dragger', extraArgs=[menu,me,xOff,yOff])
				#me.dragSound.setLoop(True)
				#me.dragSound.play()
		if kind in ('button', 'radioBTN', 'checkBox'):
			try:
				f = item['func']
				funcDict=dict(inspect.getmembers(me.menuRoot.context))
				if 'args' in item and item['args'] !=None:
					if ',' in item['args']: args = item['args'].split(',')
					else: args = [item['args']]
					funcDict[f](selfPac, *args)
				else:
					funcDict[f](selfPac)
			except:
				printf(selfPac)
	if pos=='simClk': itm.setState(SUBDUED) # this is for when checkAll or unCheckAll invokes this.


def onRelease(itm, pos) :
	taskMgr.remove('dragger')
	me = itm.getPythonTag("extras")
	""" JUSTIN: This code crashes since 'str' object (me) has no attribute dragSound
	if me.dragSound:
		me.dragSound.setLoop(False)
		me.dragSound.setPlayRate(0)
	"""
	if itm.getState()!=DORMANT: itm.setState(HOVER)

	

def getTextSize(txt, style):
	tn = TextNode(txt)
	tn.setText(txt)
	tn.setFont(loader.loadFont(style['font']))
	tn.setSlant(style['slant'])
	#tn.setFont(style['font'])
	fontSize = style['font-size']
	lineHeight = tn.getLineHeight()
	f = tn.getFrameActual()
	return (tn.getWidth()*fontSize,\
		(f[3]-f[2])*fontSize,\
		lineHeight*fontSize,\
		(0, f[1]*fontSize, f[2]*fontSize, f[3]*fontSize))

def getSelectors(item, state=None):
	if state: slctrs = ['menu '+item['kind']+' :'+stateName[state].lower()]
	else: slctrs = ['menu '+item['kind']]
	if 'class' in item:
		slctrs.append('.'+item['class'])
	if 'id' in item: # id after class: id has higher priority
		slctrs.append('#'+item['id'])
	return slctrs

class MenuItem(PGItem):
	def __init__(self, menuRoot, item, cssFName=None, toggle='off'):
		PGItem.__init__(self, item['txt'])
		PGItem.setPythonTag(self, "extras", self)
		self.item = item
		self.menuRoot = menuRoot
		self.cssFName = cssFName
		self.dragSound = None
		if item['kind'] in ('checkBox', 'radioBTN'):
			tt = item['txt'].split('\n')
			ll = len(tt)
			ttt = ''
			for t in tt:
				ttt += checkBoxShim*ll + t + '\n' # make room for checkbox)
			item['txt'] = ttt[:-1] #remove last new-line
			self.setTag('toggle', toggle)
		self.style = getStyle(getSelectors(item), self.cssFName)
		width, height, lineHeight,fr = getTextSize(item['txt'], self.style)
		self.setFrame(fr)
		if item['kind']=='separator':
			sh = self.style['height']*self.style['font-size']
			self.setFrame(0,width, -sh/2, sh/2) 
		fs=PGFrameStyle() 
		fs.setType(PGFrameStyle.TNone) 
		self.setFrameStyle(0, fs) 
		self.setTag('id', item['id'])
		if 'groupID' in item: self.setTag('groupID', item['groupID'])

		###
		self.clickAccepted = False  #JUSTIN'S INSERTED CODE
		

	def abandon(self):# and all descendents
		c = NodePath(self).find('-PandaNode')
		if c:
			for child in c.getChildren():
				child.node().getPythonTag('extras').abandon() # abandon descendents
		#print 'abandoning-- ', self
		self.setPythonTag("extras", 'done') # abandon self

	def deformat(self):
		""" Used when menu is modified with insertAfter, itemDelete, etc.
		Needed to restore frame to 'ground state' to allow proper reformating in itmFinish."""
		me = self.getPythonTag("extras")
		itm = me.item
		w, h, lH, frame = getTextSize(itm['txt'], me.style)
		self.setFrame(frame) 

	def finish(self, pos=(0,0,0), minWidth=1):
		"""
		adjust frame for uniform width with siblings
		adjust pos relative to parent or older sibs
		attach stateGraphics
		"""
		me = self.getPythonTag("extras")
		item = me.item
		scale = me.style['font-size']
		kind=item['kind']
		width, height, lineHeight, fram = getTextSize(item['txt'], me.style)
		width = max(width,minWidth)
		arrowhead=.5*lineHeight
		padding = me.style['padding']
		padding = (padding[0]*scale ,padding[1]*scale ,padding[2]*scale ,padding[3]*scale )
		bevel = me.style['bevel']*scale 
		multiLineShim = 0
		if '\n' in item['txt']: multiLineShim = .04 # might need to change this to fit font
		NodePath(self).setPos(pos)
		if kind=='separator':
			sh = me.style['height']*scale 
			frame=(	-padding[0], width+padding[1], -sh/2, sh/2)
		else:
			frame = (fram[0],max(fram[1],fram[0]+minWidth),fram[2],fram[3]) 
			frame=(	frame[0]-padding[0],
					frame[1]+padding[1],
					frame[2]-padding[2]-multiLineShim,
					frame[3]+padding[3])
			stateGraphics = getBackgroundSet(self, frame, arrowhead)
			for state in STATES:
					self.clearStateDef(state) # in case we've been here befor
					self.instanceToStateDef(state, stateGraphics[state])
			DO=DirectObject()
			if not self.clickAccepted: #JUSTIN'S INSERTED CODE
                                DO.accept(self.getEnterEvent(), onEnter, [me.menuRoot.menuRootID, self]) 
                                DO.accept(self.getExitEvent(), onLeave, [me.menuRoot.menuRootID, self])
			if kind in ('button', 'checkBox', 'radioBTN', 'checkAllBTN', 'unCheckAllBTN', 'titleBar', 'close'):
                                if not self.clickAccepted: #JUSTIN'S INSERTED CODE
                                        DO.accept(self.getPressEvent(MouseButton.one()), onPress, [self]) 
                                        DO.accept(self.getReleaseEvent(MouseButton.one()), onRelease, [self]) 
                                        # so we can simulate 'click' with messenger.send('press'+id, ['simClk']):
                                        DO.accept('press'+item['id'], onPress, [self])

                        if not self.clickAccepted: #JUSTIN'S INSERTED CODE
                                self.clickAccepted=True
			self.setActive(True)

		if kind == 'parent':# accomodate arrowheads
			self.setFrame(frame[0], frame[1]+arrowhead*2-bevel, frame[2], frame[3])
		else:
			self.setFrame(frame)

#mySound = base.loader.loadSfx("path/to/sound_file.ogg")
	def getFMargin(self):
		return self.style['margin']

	def getFFrame(self):
		s = self.style['font-size']
		f = self.getFrame()
		m = self.style['margin']
		 # return copy to avoid side effects
		return (f[0]-m[0]*s, f[1]+m[1]*s, f[2]-m[2]*s, f[3]+m[3]*s)

	def getFWidth(self):
		s = self.style['font-size']
		f = self.getFrame()
		m = self.style['margin']
		return f[1]-f[0]+(m[0]+m[1])*s

	def getFHeight(self):
		s = self.style['font-size']
		f = self.getFrame()
		m = self.style['margin']
		return f[3]-f[2]+(m[2]+m[3])*s

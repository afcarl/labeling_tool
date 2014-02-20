"""
This module manages the SQL database
"""

import time
import traceback
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
MATCH_TIMEOUT = 200 #seconds

engine = create_engine('sqlite:///uploads.db',echo=False)
Session = sessionmaker(bind=engine)
session = Session()	

class PendingMatch(Base):
	__tablename__ = 'pending'
	id = Column(Integer, primary_key=True)
	last_issued = Column(Integer)
	pcname = Column(String)
	image = Column(String)
	camera = Column(String)
	objects = Column(String)

	def addObject(self, obj):
		l = eval(self.objects)
		if obj in l:
			return
		l.append(obj)
		self.objects = str(l)

	def removeObject(self, obj):
		l = eval(self.objects)
		if not obj in l:
			return len(l)
		l.remove(obj)
		self.objects = str(l)
		return len(l)

	def __repr__(self):
		return "<PendMatch(pc='%s', objs='%s', last_issued='%s', id='%s')>" % (self.pcname,
		 self.objects, self.last_issued, self.id)

class Match(Base):
	__tablename__ = 'matches'
	id = Column(Integer, primary_key=True)
	pcname = Column(String)
	meshname = Column(String)
	matrix = Column(String)
	username = Column(String)
	other = Column(String)

	def __repr__(self):
		return "<Match(pc='%s', mesh='%s', mat='%s', id='%s')>" % (self.pcname,
		 self.meshname, self.matrix, self.id)

"""
Returns a pending match that has not been issued in the last MATCH_TIMOUT seconds
as a [pcname, list_of_objects, image, camera] list.
"""
def getPendingMatch():
	curTime = int(time.time())
	pend = session.query(PendingMatch).filter(PendingMatch.last_issued < 
		curTime - MATCH_TIMEOUT).first() 
	if pend:	
		pend.last_issued = curTime
		session.commit()
		return [ pend.pcname, pend.objects, pend.image, pend.camera]
	else:
		return None

"""
Add a scene to the list of pending matches.
pcname_ is a string corresponding to the filename of the point cloud
objects_ is a python list 
"""
def addScene(pcname_, objects_, img, cam):
	match = session.query(PendingMatch).filter_by(pcname=pcname_).first() 
	if match is None: #new scene definition
		p = PendingMatch(pcname=pcname_, objects=str(objects_), last_issued=int(0),
			image = img, camera = cam)
		session.add(p)
	else: #update old scene definition
		match.image = img #override old image
		match.camera = cam #override old camera
		for o in objects_:
			match.addObject(o)


def registerMatch(pcname_, meshname_, matrix_, user_, other_= None):
	curTime = int(time.time())
	matrix_ = str(matrix_)
	match = session.query(PendingMatch).filter_by(pcname=pcname_).first() 
	if match:
		size_ = match.removeObject(meshname_)
		if size_ == 0:
			session.delete(match)

		oldmatch = session.query(Match).filter_by(pcname=pcname_, meshname = meshname_).first() 		
		if oldmatch:
			oldmatch.matrix = matrix_	
			oldmatch.other = str(other_)
		else:
			m = Match(pcname=pcname_, meshname = meshname_,matrix =matrix_, username=user_ other=str(other_))
			session.add(m)

	session.commit()

def getMatchStr( pcname_, meshname_):
	match = session.query(Match).filter_by(pcname=pcname_, meshname = meshname_).first() 		
	if not match:
		return None
	s = 'pcname = '+match.pcname+'\n'
	s += 'mesh = '+match.meshname+'\n'
	s += "matrix = "+ match.matrix+'\n'
	s += "username = "+ match.username+'\n'

    #write other fields
	if (not match.other) or (len(match.other) == 0):
		return s
	try:
		other = eval(match.other)
		if other:
		    for k in other:
		        s += k+" = "+str(other[k])+"\n"
		return s
	except SyntaxError as e:
		print("ERROR in evaluating other field of database entry ",match)
		traceback.print_exc()
		return s
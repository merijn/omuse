import numpy

from amuse.units import units

from amuse.datamodel import Grid

class adcirc_file_reader(file):
  def read_string(self,n=80):
    return self.readline()[:n]
  def read_int(self,n=1):
    result=[int(l) for l in self.readline().split()[:n]]
    return result[0] if len(result)==1 else result    
  def read_value(self, *types):
    if len(types)==0: types=(float,)
    result=[x(l) for x,l in zip(types,self.readline().split())]    
    return result[0] if len(result)==1 else result    
  def read_single_type_attributes(self,n,m,dtype=int):
    result=numpy.zeros((n,m),dtype)
    _n=0
    while _n<n:
      line_=self.readline().split()
      index=int(line_[0])-1
      result[index,:]=[float(line_[i]) for i in range(1,m+1)]
      _n+=1    
    return result
  def read_boundary_segment(self,n):
    seg=[]
    i=0
    while i<n:
      line=self.readline()
      line_=line.split()
      seg.append( int(line_[0]))
      i+=1
    return numpy.array(seg)    
  def read_boundary_segments(self,nseg,nnodes,default_type=None):
    i=0
    _nnodes=0
    result=[]
    while i<nseg:
      line=self.readline()
      line_=line.split()
      n=int(line_[0])
      if default_type is not None:
        _type=default_type
      else:
        _type=int(line_[1])
      _nnodes+=n
      seg=self.read_boundary_segment(n)
      i+=1
      result.append((_type,seg))
    assert nnodes==_nnodes
    return result

class adcirc_parameter_reader(object):  
  def __init__(self,filename="fort.15"):
    self.filename=filename
  
  def read_parameters(self):
    f=adcirc_file_reader(self.filename,'r')
    param=dict()
    param["RUNDES"]=f.read_string(32)    
    param["RUNDID"]=f.read_string(24)    
    param["NFOVER"]=f.read_int()
    param["NABOUT"]=f.read_int()
    param["NSCREEN"]=f.read_int()
    param["IHOT"]=f.read_int()
    param["ICS"]=f.read_int()
    param["IM"]=f.read_int()
    if param["IM"] in [20,30]:
      param["IDEN"]=f.read_int()
    else:
      param["IDEN"]=None
    param["NOLIBF"]=f.read_int()
    param["NOLIFA"]=f.read_int()
    param["NOLICA"]=f.read_int()
    param["NOLICAT"]=f.read_int()
    param["NWP"]=f.read_int()
    param["AttrName"]=[]
    for i in range(param["NWP"]):
      param["AttrName"].append(f.read_string(80))
    param["NCOR"]=f.read_int()
    param["NTIP"]=f.read_int()
    param["NWS"]=f.read_int()
    param["NRAMP"]=f.read_int()
    param["G"]=f.read_value()    
    param["TAU0"]=f.read_value()
    if param["TAU0"]==-5.0:
      _x,_y=f.read_value(float,float)
      param["Tau0FullDomainMin"]=_x
      param["Tau0FullDomainMax"]=_y
    else:
      param["Tau0FullDomainMin"]=None
      param["Tau0FullDomainMax"]=None
    param["DTDP"]=f.read_value()
    param["STATIM"]=f.read_value()
    param["REFTIM"]=f.read_value()
#~ WTIMINC  Supplemental Meteorological/Wave/Ice Parameters Line
    param["RNDAY"]=f.read_value()
    if param["NRAMP"] in [0,1]:
      param["DRAMP"]=f.read_value()
    elif param["NRAMP"] in [2,3,4,5,6,7,8]:
      raise Exception("tbd")
    else:
      param["DRAMP"]=None
    param["A00"],param["B00"],param["C00"]=f.read_value(float,float,float)


#~ H0  include this line if NOLIFA =0, 1
#~ H0, INTEGER, INTEGER, VELMIN  include this line if NOLIFA =2, 3
#~ SLAM0, SFEA0
#~ TAU include this line only if NOLIBF = 0
#~ CF  include this line only if NOLIBF =1
#~ CF, HBREAK, FTHETA, FGAMMA  include this line only if NOLIBF =2
#~ ESLM  include this line only if IM =0, 1, 2
#~ ESLM, ESLC  include this line only if IM =10
#~ CORI
#~ NTIF

      

    self.parameters=param
    
class adcirc_grid_reader(object):
  
  def __init__(self,filename="fort.14"):
    self.filename=filename
    self.unit_length = units.m
    self.unit_position = units.m

  def read_grid(self):
    f=adcirc_file_reader(self.filename,'r')
    param=dict()
    param["AGRID"]=f.read_string()

    NE,NP=f.read_int(2)
    
    self.p=f.read_single_type_attributes(NP,3,float)
    self.t=f.read_single_type_attributes(NE,4,int)

    assert numpy.all(self.t[:,0]==3)
            
    NOPE=f.read_int(1)
    NETA=f.read_int(1)

    self.elev_spec_boundary_seg=f.read_boundary_segments(NOPE,NETA,0)

    NBOU=f.read_int(1)
    NVEL=f.read_int(1)
    self.flow_spec_boundary_seg=f.read_boundary_segments(NBOU,NVEL)
    
    param["NE"]=NE
    param["NP"]=NP
    param["NOPE"]=NOPE
    param["NBOU"]=NBOU
    self.parameters=param
        
    f.close()

  def get_sets(self):
    nodes=Grid(self.parameters["NP"])
    nodes.x=self.p[:,0] | self.unit_position
    nodes.y=self.p[:,1] | self.unit_position
    nodes.depth=self.p[:,2] | self.unit_length
        
    elements=Grid(self.parameters["NE"])
    elements.nodes=[(x[1]-1,x[2]-1,x[3]-1) for x in self.t]
    
    boundary=[]
    for type_,seg in self.elev_spec_boundary_seg:
      indices=seg-1
      boundary.append(dict(nodes=indices,btype="elev",subtype=type_))
    for type_,seg in self.flow_spec_boundary_seg:
      indices=seg-1
      boundary.append(dict(nodes=indices,btype="flow",subtype=type_))
    
    return nodes,elements,boundary
  
def assign_neighbours(nodes,elements):  
    for n in nodes:
      n.neighbours=set()
    
    for e in elements:
      p1=e.nodes[0]
      p2=e.nodes[1]
      p3=e.nodes[2]
      nodes[p1].neighbours.add(p2)
      nodes[p1].neighbours.add(p3)
      nodes[p2].neighbours.add(p1)
      nodes[p2].neighbours.add(p3)
      nodes[p3].neighbours.add(p1)
      nodes[p3].neighbours.add(p2)
     
def get_edges(elements):
    edges=set()
    for e in elements:
      for i,j in [(0,1),(1,2),(2,0)]:
        edges.add( frozenset([e.nodes[i],e.nodes[j]]) )
    return edges

a=adcirc_grid_reader()
a.read_grid()
nodes,elements,boundary=a.get_sets()
assign_neighbours(nodes,elements)
edges=get_edges(elements)

print nodes[1].neighbours
print 
print elements
print
print boundary

a=adcirc_parameter_reader()
a.read_parameters()
print a.parameters

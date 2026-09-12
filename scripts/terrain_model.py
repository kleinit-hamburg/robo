"""Small deterministic terrain fixtures, not calibrated Kirchwerder soil."""
import math
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
PROFILES=('garden','flat','engineering','manipulation','plant','potato_ridge','uneven','slope','slippery','obstacle')
def terrain(world,profile):
    def material(node,color):
        E.SubElement(E.SubElement(node,'material'),'diffuse').text=color
    def friction(node,mu='0.6'):
        ode=E.SubElement(E.SubElement(E.SubElement(node,'surface'),'friction'),'ode');E.SubElement(ode,'mu').text=mu;E.SubElement(ode,'mu2').text=mu
    def model_link(name,xyz):
        model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text=' '.join(map(str,(*xyz,0,0,0)))
        return E.SubElement(model,'link',name='link')
    def geom(parent,kind,shape,dims,pose=(0,0,0,0,0,0),color='0.48 0.38 0.25 1',mu='0.6'):
        tag='collision' if kind.startswith('collision') else 'visual'
        node=E.SubElement(parent,tag,name=kind);E.SubElement(node,'pose').text=' '.join(map(str,pose));g=E.SubElement(node,'geometry')
        if shape=='box':E.SubElement(E.SubElement(g,'box'),'size').text=' '.join(map(str,dims))
        elif shape=='sphere':E.SubElement(E.SubElement(g,'sphere'),'radius').text=str(dims[0])
        elif shape=='cylinder':
            c=E.SubElement(g,'cylinder');E.SubElement(c,'radius').text=str(dims[0]);E.SubElement(c,'length').text=str(dims[1])
        elif shape=='mesh':
            mesh=E.SubElement(g,'mesh');E.SubElement(mesh,'uri').text='file://'+str((ROOT/dims[0]).resolve())
            if len(dims)>1:E.SubElement(mesh,'scale').text=' '.join(map(str,dims[1]))
        else:raise ValueError(shape)
        if tag=='visual':material(node,color)
        else:friction(node,mu)
    def box(name,xyz,size,pitch=0):
        model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text=' '.join(map(str,(*xyz,0,pitch,0)))
        link=E.SubElement(model,'link',name='link')
        geom(link,'visual','box',size,color='0.48 0.38 0.25 1')
        geom(link,'collision','box',size)
    def potato_plant(name,x,y):
        link=model_link(name,(x,y,0))
        geom(link,'collision','cylinder',(.035,.32),(0,0,.16,0,0,0),mu='0.2')
        geom(link,'visual_haulm_mesh','mesh',('assets/visual/potato_haulm.glb',(1,1,1)),(0,0,0,0,0,0),'0.20 0.42 0.16 1')
    def weed(name,x,y,root_peak='75'):
        link=model_link(name,(x,y,0))
        geom(link,'collision','cylinder',(.018,.18),(0,0,.09,0,0,0),mu='0.35')
        geom(link,'visual_weed_mesh','mesh',('assets/visual/weed_broadleaf.glb',(1,1,1)),(0,0,0,0,0,0),'0.25 0.55 0.18 1')
    if profile=='uneven':
        for n in range(24):
            top=.01+.01*math.sin(n*math.pi/4)
            box(f'undulation_{n}',(.55+n*.06,-.8,top-.025),(.06,1.,.05))
    elif profile=='slope':
        a=math.radians(5);height=1.5*math.sin(a)
        box('slope_5deg',(1.25,-.8,.75*math.sin(a)-.0125*math.cos(a)),(1.5,1.,.025),-a)
        box('slope_landing',(2.32,-.8,height/2),(.7,1.,height))
    elif profile=='obstacle':box('threshold_20mm',(.9,-.8,.01),(.08,1.,.02))

    elif profile=='potato_ridge':
        # Kirchwerder potato-row fixture: 62 cm row spacing, about 15 cm ridge height.
        # Visuals are richer than collisions; physics remains simple and deterministic.
        for y,name in ((-.31,'left'),(.31,'right')):
            link=model_link(f'potato_{name}_ridge',(1.45,y,0))
            geom(link,'collision','box',(3.4,.34,.15),(0,0,.075,0,0,0),mu='0.45')
            geom(link,'visual_ridge_mesh','mesh',('assets/visual/potato_ridge_340cm.glb',(1,1,1)),(0,0,0,0,0,0),'0.50 0.36 0.21 1')
            for i,x in enumerate((.45,.95,1.45,1.95,2.45)):
                potato_plant(f'potato_{name}_plant_{i}',x,y)
        for i,(x,y) in enumerate(((.70,-.18),(1.10,.13),(1.55,-.12),(2.05,.18),(2.40,-.05))):
            weed(f'weed_between_ridges_{i}',x,y)
        for i,x in enumerate((.55,1.35,2.15)):
            link=model_link(f'soil_clod_{i}',(x,.02,.025))
            geom(link,'collision','sphere',(.035,),(0,0,0,0,0,0),mu='0.45')
            geom(link,'visual','sphere',(.045,),(0,0,0,0,0,0),'0.34 0.24 0.15 1')
    elif profile=='engineering':
        for x,h,name in ((.65,.03,'stone_30mm'),(1.05,.05,'stone_50mm'),(1.55,.08,'stone_80mm')):box(name,(x,-.8,h/2),(.16,.9,h))
        a=math.radians(20);box('ramp_20deg',(2.25,-.8,.35*math.sin(a)-.02*math.cos(a)),(.7,.9,.04),-a)
        box('narrow_gate_left',(3.1,-.27,.18),(.45,.06,.36));box('narrow_gate_right',(3.1,-1.33,.18),(.45,.06,.36))

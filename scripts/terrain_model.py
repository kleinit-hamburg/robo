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
    def model_link(name,xyz,rpy=(0,0,0)):
        model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text=' '.join(map(str,(*xyz,*rpy)))
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
    def potato_plant(name,x,y,yaw=0,scale=1):
        link=model_link(name,(x,y,0),(0,0,yaw))
        geom(link,'collision','cylinder',(.035,.32),(0,0,.16,0,0,0),mu='0.2')
        variant='potato_haulm.glb' if int(abs(x*100)+abs(y*100))%3==0 else 'potato_haulm_b.glb' if int(abs(x*100)+abs(y*100))%3==1 else 'potato_haulm_c.glb'
        geom(link,'visual_haulm_mesh','mesh',('assets/visual/'+variant,(scale,scale,scale)),(0,0,0,0,0,0),'0.20 0.42 0.16 1')
    def weed(name,x,y,yaw=0,scale=1,root_peak='75'):
        link=model_link(name,(x,y,0),(0,0,yaw))
        geom(link,'collision','cylinder',(.018,.18),(0,0,.09,0,0,0),mu='0.35')
        geom(link,'visual_weed_mesh','mesh',('assets/visual/weed_broadleaf.glb',(scale,scale,scale)),(0,0,0,0,0,0),'0.25 0.55 0.18 1')
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
        soil=model_link('visual_soil_surface',(0,0,.002))
        geom(soil,'visual_soil_mesh','mesh',('assets/visual/soil_patch_7x5.glb',(1,1,1)),(0,0,0,0,0,0),'0.34 0.25 0.16 1')
        rows=[(-1.24,'outer_left'),(-.62,'left'),(0.0,'center'),(.62,'right'),(1.24,'outer_right')]
        for row_index,(y,name) in enumerate(rows):
            link=model_link(f'potato_{name}_ridge',(1.65,y,0))
            geom(link,'collision','box',(4.4,.34,.15),(0,0,.075,0,0,0),mu='0.45')
            geom(link,'visual_ridge_mesh','mesh',('assets/visual/potato_ridge_340cm.glb',(1.30,1,1)),(0,0,0,0,0,0),'0.50 0.36 0.21 1')
            for i,x in enumerate((.10,.70,1.30,1.90,2.50,3.10)):
                potato_plant(f'potato_{name}_plant_{i}',x,y,yaw=(i*.71 + row_index*.19),scale=.82+.05*((i+row_index)%3))
        weed_positions=[]
        for lane_y in (-.93,-.31,.31,.93):
            for j,x in enumerate((.35,.95,1.55,2.15,2.75,3.35)):
                weed_positions.append((x,lane_y+(.035 if j%2 else -.04)))
        for i,(x,y) in enumerate(weed_positions):
            weed(f'weed_between_ridges_{i}',x,y,yaw=i*.83,scale=.68+.07*(i%4))
        for i,(x,y) in enumerate(((.55,-.31),(1.35,.31),(2.15,-.93),(2.85,.93),(3.25,.0))):
            link=model_link(f'soil_clod_{i}',(x,y,.025))
            geom(link,'collision','sphere',(.035,),(0,0,0,0,0,0),mu='0.45')
            geom(link,'visual','sphere',(.045,),(0,0,0,0,0,0),'0.34 0.24 0.15 1')
    elif profile=='engineering':
        for x,h,name in ((.65,.03,'stone_30mm'),(1.05,.05,'stone_50mm'),(1.55,.08,'stone_80mm')):box(name,(x,-.8,h/2),(.16,.9,h))
        a=math.radians(20);box('ramp_20deg',(2.25,-.8,.35*math.sin(a)-.02*math.cos(a)),(.7,.9,.04),-a)
        box('narrow_gate_left',(3.1,-.27,.18),(.45,.06,.36));box('narrow_gate_right',(3.1,-1.33,.18),(.45,.06,.36))

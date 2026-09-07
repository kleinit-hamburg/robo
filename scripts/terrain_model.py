"""Small deterministic terrain fixtures, not calibrated Kirchwerder soil."""
import math
import xml.etree.ElementTree as E
PROFILES=('garden','flat','manipulation','plant','uneven','slope','slippery','obstacle')
def terrain(world,profile):
    def box(name,xyz,size,pitch=0):
        model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text=' '.join(map(str,(*xyz,0,pitch,0)))
        link=E.SubElement(model,'link',name='link')
        for kind in ('visual','collision'):
            node=E.SubElement(link,kind,name=kind);E.SubElement(E.SubElement(E.SubElement(node,'geometry'),'box'),'size').text=' '.join(map(str,size))
            if kind=='visual':E.SubElement(E.SubElement(node,'material'),'diffuse').text='0.48 0.38 0.25 1'
            else:
                ode=E.SubElement(E.SubElement(E.SubElement(node,'surface'),'friction'),'ode');E.SubElement(ode,'mu').text='0.6';E.SubElement(ode,'mu2').text='0.6'
    if profile=='uneven':
        for n in range(24):
            top=.01+.01*math.sin(n*math.pi/4)
            box(f'undulation_{n}',(.55+n*.06,-.8,top-.025),(.06,1.,.05))
    elif profile=='slope':
        a=math.radians(5);height=1.5*math.sin(a)
        box('slope_5deg',(1.25,-.8,.75*math.sin(a)-.0125*math.cos(a)),(1.5,1.,.025),-a)
        box('slope_landing',(2.32,-.8,height/2),(.7,1.,height))
    elif profile=='obstacle':box('threshold_20mm',(.9,-.8,.01),(.08,1.,.02))

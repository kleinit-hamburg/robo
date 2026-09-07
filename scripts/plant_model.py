"""Single 8 mm rigid weed stem for a known-target mechanics fixture."""
import xml.etree.ElementTree as E
from arm_model import element

def add_plant(world):
    model=element(world,'model',name='weed');element(model,'pose','.96 -.8 .11 0 0 0')
    stem=element(model,'link',name='stem');inertial=element(stem,'inertial');element(inertial,'mass',.2);inertia=element(inertial,'inertia')
    for k,v in {'ixx':.00080747,'iyy':.00080747,'izz':.0000016}.items():element(inertia,k,v)
    for kind in ('visual','collision'):
        part=element(stem,kind,name='stem_'+kind);geo=element(element(part,'geometry'),'cylinder');element(geo,'radius',.004);element(geo,'length',.22)
        if kind=='visual':element(element(part,'material'),'diffuse','0.15 0.65 0.12 1')
        else:
            ode=element(element(element(part,'surface'),'friction'),'ode');element(ode,'mu',.5);element(ode,'mu2',.5)

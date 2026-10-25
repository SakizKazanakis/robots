"""Preliminary parametric plywood plate. NOT verified for manufacture."""
import cadquery as cq

def plate(length=95.0,height=34.0,thickness=6.5,window=True):
    assert length>2*height and height>=25 and thickness>0
    part=cq.Workplane("XZ").center(length/2,0).rect(length,height).extrude(thickness)
    if window:
        part=part.faces(">Y").workplane().center(0,0).rect(length-2*height,height-18).cutThruAll()
    return part.val()

def pair(length,thickness=6.5,gap=25.0):
    part=plate(length,thickness=thickness)
    return [part.translate((0,-gap/2,0)),part.translate((0,gap/2+thickness,0))]

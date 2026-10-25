"""Engineering reference solids for plywood/aluminum comparisons, NOT release parts."""
from pathlib import Path
import cadquery as cq
from .hybrid import plate

def aluminum_link(length,height=34,thickness=3):
    return plate(length,height,thickness)

def chassis(length=280,width=190,wall=5,height=40):
    assert 2*wall<min(length,width)
    return cq.Workplane("XY").box(length,width,height).faces(">Z").shell(-wall).val()

def payload(length=95,width=85,thickness=5,pitch=40,diameter=4.5):
    assert pitch+diameter<min(length,width)
    return (cq.Workplane("XY").box(length,width,thickness).faces(">Z").workplane()
            .pushPoints([(x,y) for x in [-pitch/2,pitch/2] for y in [-pitch/2,pitch/2]])
            .hole(diameter).val())

def export(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    objects={
        "FEMUR_PLYWOOD":plate(95,thickness=6.5),
        "TIBIA_PLYWOOD":plate(110,thickness=6.5),
        "FEMUR_ALUMINUM":aluminum_link(95),
        "TIBIA_ALUMINUM":aluminum_link(110),
        "CHASSIS_H6_ENVELOPE":chassis(),
        "PAYLOAD_MOUNT_DRAFT":payload(),
    }
    results={}
    for name,part in objects.items():
        assert part.isValid() and part.Volume()>0
        filename=out/(name+".step")
        cq.exporters.export(part,str(filename))
        reloaded=cq.importers.importStep(str(filename)).val()
        assert reloaded.isValid()
        results[name]={"volume_mm3":round(part.Volume(),2),"step_valid":True}
    return results

if __name__=="__main__":
    import json
    print(json.dumps(export("out"),indent=2))

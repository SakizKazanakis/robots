"""AK45-10 V3.0 joint cartridge engineering candidate; NOT FOR MANUFACTURE.
All bearing seats, shaft fits, fasteners and fabricated adapters remain ASSUMED.
OEM_CYLINDER_AXES captures geometric cylinder axes inspected in official OEM STEP;
no thread, function, interference-fit or allowable load has been established.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json,math
import cadquery as cq

OEM_CYLINDER_AXES={
 "housing_r1p4_y27p2":[(0,27.2,23.5),(0,27.2,-23.5),(23.5,27.2,0),(-23.5,27.2,0)],
 "output_r1p1_y32p7":[(22.962,32.7,5),(-22.962,32.7,5),(5,32.7,22.962),(5,32.7,-22.962)],
 "rear_r1p35_y_minus6p5":[(0,-6.5,23.75),(20.568,-6.5,-11.875),(-20.568,-6.5,-11.875)]
}
@dataclass(frozen=True)
class Joint:
 adapter_od:float=72.
 adapter_t:float=7.
 housing_od:float=69.
 housing_t:float=12.
 bearing_seat_od:float=42.
 bearing_seat_depth:float=7.
 pin_d:float=25.
 pin_length:float=82.
 bearing_id:float=25.
 gap:float=62.
 bolt_pcd:float=47.
 bolt_d:float=4.
 def validate(self):
  if not self.adapter_od>self.housing_od>self.bearing_seat_od>self.pin_d>0:raise ValueError("diameters")
  if self.housing_t<=self.bearing_seat_depth:raise ValueError("seat depth")
  if self.pin_length<self.gap+10:raise ValueError("pin length")
  if self.bolt_pcd+self.bolt_d>=self.adapter_od:raise ValueError("bolt pattern")
def ring(od,id,t):return cq.Workplane("XY").circle(od/2).circle(id/2).extrude(t).val()
def components(p):
 p.validate()
 adapter=cq.Workplane("XY").circle(p.adapter_od/2).circle((p.pin_d+1)/2).extrude(p.adapter_t)
 pts=[(p.bolt_pcd/2*math.cos(k*math.pi/2),p.bolt_pcd/2*math.sin(k*math.pi/2)) for k in range(4)]
 adapter=adapter.faces(">Z").workplane().pushPoints(pts).hole(p.bolt_d).val()
 housing=(cq.Workplane("XY").circle(p.housing_od/2).extrude(p.housing_t)
          .faces(">Z").workplane().hole(p.bearing_id+1)
          .faces(">Z").workplane().circle(p.bearing_seat_od/2)
          .cutBlind(-p.bearing_seat_depth).val())
 pin=cq.Solid.makeCylinder(p.pin_d/2,p.pin_length)
 lug=(cq.Workplane("XY").rect(32,44).extrude(7)
      .faces(">Z").workplane().hole(p.pin_d+1).val())
 return {
  "motor_ENVELOPE":cq.Solid.makeCylinder(26.5,45.2).translate((0,0,-22.6)),
  "output_adapter_ASSUMED":adapter.translate((0,0,23.6)),
  "opposite_bearing_housing_ASSUMED":housing.translate((0,0,-p.gap/2-p.housing_t)),
  "shaft_envelope_ASSUMED":pin.translate((0,0,-p.pin_length/2)),
  "link_lug_ASSUMED":lug.translate((0,0,p.gap/2+9)),
  "washer_one_ASSUMED":ring(34,p.pin_d+1,2.5).translate((0,0,p.gap/2+7)),
  "washer_two_ASSUMED":ring(34,p.pin_d+1,2.5).translate((0,0,-p.gap/2-3))}
def export(p,out):
 p.validate();d=Path(out);d.mkdir(parents=True,exist_ok=True)
 colors=[cq.Color(.14,.18,.23),cq.Color(.93,.47,.18),cq.Color(.55,.63,.73),
         cq.Color(.72,.75,.80),cq.Color(.74,.54,.32),cq.Color(.75,.78,.83),cq.Color(.75,.78,.83)]
 ass=cq.Assembly(name="SPIDER_JOINT_CARTRIDGE_v05_DRAFT")
 data={"status":"GEOMETRY_VALID_ONLY_NOT_MANUFACTURING_READY",
       "oem_cylinder_axes":OEM_CYLINDER_AXES,"assumed":asdict(p),
       "limits":["OEM hole functionality NOT verified","bearing catalog selection missing",
                 "shaft/output drive coupling missing","fits and tolerances missing",
                 "full assembly clearance and structural loads NOT verified"],"parts":{}}
 for (name,sh),color in zip(components(p).items(),colors):
  if not sh.isValid() or sh.Volume()<=0:raise ValueError(name)
  ass.add(sh,name=name,color=color)
  path=d/(name+".step");cq.exporters.export(sh,str(path),exportType="STEP")
  if not cq.importers.importStep(str(path)).val().isValid():raise ValueError(name+" STEP")
  data["parts"][name]=round(sh.Volume(),2)
 path=d/"SPIDER_JOINT_CARTRIDGE_v05_DRAFT.step"
 ass.save(str(path),exportType="STEP")
 if not cq.importers.importStep(str(path)).val().isValid():raise ValueError("Assembly STEP")
 (d/"JOINT_CARTRIDGE_AUDIT.json").write_text(json.dumps(data,indent=2)+"\n")
 return data
if __name__=="__main__":
 import argparse
 a=argparse.ArgumentParser();a.add_argument("--out",default="out")
 print(json.dumps(export(Joint(),a.parse_args().out),indent=2))

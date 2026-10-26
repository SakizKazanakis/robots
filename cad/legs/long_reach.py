"""Long-reach skeletal leg CAD. DRAFT ONLY. No OEM mounting holes or released drawings.

This module uses cad/parameters.json as the common H6/Q4 kinematic source.
Joint/actuator interfaces, bearings, cable routing, FEA and real performance
are NOT qualified. STEP/DXF show only reference geometry, not manufactured fits.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse, json, math
import cadquery as cq

@dataclass(frozen=True)
class LegDesign:
    coxa: float = 90.0
    femur: float = 135.0
    tibia: float = 160.0
    hip_deg: float = 35.0
    knee_deg: float = 90.0
    plate_thickness: float = 6.5
    aluminum_thickness: float = 3.0
    plate_gap: float = 60.0
    width_root: float = 44.0
    width_middle: float = 38.0
    width_tip: float = 39.0
    window_width: float = 11.0
    spacer_outer_diameter: float = 13.0
    spacer_bore_diameter: float = 5.5
    spacer_hole_diameter: float = 5.5
    motor_diameter: float = 53.0
    motor_depth: float = 45.2
    foot_radius: float = 13.0
    assumed_robot_mass_kg: float = 7.506
    gravity: float = 9.81
    body_underside_z: float = -60.0
    assumed_plywood_density_kg_m3: float = 680.0
    assumed_aluminum_density_kg_m3: float = 2700.0

    def validate(self):
        if min(self.coxa-70,self.femur-105,self.tibia-120)<0: raise ValueError("Link envelopes too short")
        if not (0<self.plate_thickness<15 and 1<self.aluminum_thickness<12):
            raise ValueError("Plate thickness")
        if self.plate_gap<self.motor_depth+2: raise ValueError("Insufficient internal spacing")
        if not (25<=self.hip_deg<=55 and 55<=self.knee_deg<=120):raise ValueError("Invalid posture")
        if not (6<=self.window_width<.55*min(self.width_middle,self.width_tip)):
            raise ValueError("Window too wide")
        if self.spacer_outer_diameter<=self.spacer_bore_diameter:raise ValueError("Spacer bore")
        if self.width_root<=self.window_width or self.width_tip<=self.window_width:
            raise ValueError("Insufficient section")

def outer_vertices(span,p):
    r,wm,wt=p.width_root/2,p.width_middle/2,p.width_tip/2
    upper=[(-r*.80,0),(-r*.55,r*.76),(0,r),(.14*span,r),
           (.38*span,wm),(.62*span,wm*.92),(.83*span,wt),
           (span,wt),(span+wt*.64,wt*.70),(span+wt*.86,0)]
    return upper+[(x,-y) for x,y in reversed(upper[1:-1])]

def plate(span,p,material="plywood",windows=True):
    p.validate()
    if span<105 and windows:raise ValueError("Short Coxa needs independent bridge design")
    t=p.plate_thickness if material=="plywood" else p.aluminum_thickness
    w=cq.Workplane("XY").polyline(outer_vertices(span,p)).close().extrude(t)
    if windows:
        for f in (.4,.6):
            cutter=(cq.Workplane("XY").workplane(offset=-1).center(span*f,0)
                   .slot2D(span*.12,p.window_width,angle=0).extrude(t+2))
            w=w.cut(cutter)
        for f in (.27,.73):
            cutter=(cq.Workplane("XY").workplane(offset=-1).center(span*f,0)
                   .circle(p.spacer_hole_diameter/2).extrude(t+2))
            w=w.cut(cutter)
    sh=w.val()
    if not sh.isValid() or len(sh.Solids())!=1 or sh.Volume()<=0:
        raise ValueError("Invalid CAD solid")
    return sh

def spacer(p):
    return (cq.Workplane("XY").circle(p.spacer_outer_diameter/2)
            .circle(p.spacer_bore_diameter/2).extrude(p.plate_gap).val())

def cheek_pair(span,p,material="plywood",windows=True):
    t=p.plate_thickness if material=="plywood" else p.aluminum_thickness
    sh=plate(span,p,material,windows)
    return [sh.translate((0,0,p.plate_gap/2)),
            sh.translate((0,0,-p.plate_gap/2-t))]

def leg_points(p):
    a=math.radians(p.hip_deg);b=math.radians(p.hip_deg+p.knee_deg)
    return ((0,0,0),(p.coxa,0,0),
            (p.coxa+p.femur*math.cos(a),0,-p.femur*math.sin(a)),
            (p.coxa+p.femur*math.cos(a)+p.tibia*math.cos(b),0,
             -p.femur*math.sin(a)-p.tibia*math.sin(b)))

def transform(sh,origin,angle):
    return sh.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,1,0),angle).translate(origin)

def motor_envelope(p,pos,vertical=False):
    axis=cq.Vector(0,0,1) if vertical else cq.Vector(0,1,0)
    point=cq.Vector(*pos)
    return cq.Solid.makeCylinder(p.motor_diameter/2,p.motor_depth,
                                point.sub(axis.multiply(p.motor_depth/2)),axis)

def make_module(p,material="plywood"):
    p.validate()
    if material not in ("plywood","aluminum"):raise ValueError("Invalid material")
    a0,a1,a2,a3=leg_points(p)
    ass=cq.Assembly(name="LEG_"+material.upper()+"_DRAFT")
    color=cq.Color(.72,.49,.28) if material=="plywood" else cq.Color(.53,.62,.73)
    for name,origin,span,angle in (("FEMUR",a1,p.femur,p.hip_deg),
                                   ("TIBIA",a2,p.tibia,p.hip_deg+p.knee_deg)):
        for i,cheek in enumerate(cheek_pair(span,p,material),1):
            ass.add(transform(cheek,origin,angle),name=name+"_CHEEK_"+str(i),color=color)
        for i,f in enumerate((.27,.73),1):
            tube=spacer(p).translate((span*f,0,-p.plate_gap/2))
            ass.add(transform(tube,origin,angle),name=name+"_SPACER_ENVELOPE_"+str(i),
                    color=cq.Color(.69,.72,.76))
    for i,rail in enumerate(cheek_pair(p.coxa,p,"aluminum",windows=False),1):
        ass.add(transform(rail,a0,0),name="COXA_RAIL_DRAFT_"+str(i),color=cq.Color(.46,.50,.56))
    ass.add(transform(spacer(p).translate((p.coxa/2,0,-p.plate_gap/2)),a0,0),
            name="COXA_SPACER_DRAFT",color=cq.Color(.69,.72,.76))
    for name,pt,vertical in (("YAW",a0,True),("HIP",a1,False),("KNEE",a2,False)):
        ass.add(motor_envelope(p,pt,vertical),name=name+"_MOTOR_ENVELOPE_NOT_OEM",
                color=cq.Color(.18,.22,.27))
    ass.add(cq.Solid.makeSphere(p.foot_radius,cq.Vector(*a3)),name="FOOT_PLACEHOLDER",
            color=cq.Color(.14,.15,.17))
    return ass

def mass_estimate(p):
    d={}
    for m,rho in (("plywood",p.assumed_plywood_density_kg_m3),
                  ("aluminum",p.assumed_aluminum_density_kg_m3)):
        items={name+"_cheek_pair_g":round(2*plate(span,p,m).Volume()*rho/1e6,3)
               for name,span in (("femur",p.femur),("tibia",p.tibia))}
        d[m]={"status":"ASSUMED density + CALCULATED volume","items":items,
              "sum_link_plates_g":round(sum(items.values()),3)}
    return d

def moment_sweep(p):
    result={}
    for contacts in (3,6):
        f=p.assumed_robot_mass_kg*p.gravity/contacts
        cases=[]
        for hip in (25,35,45,55):
            for knee in (65,80,90,100,110,120):
                a,b=math.radians(hip),math.radians(hip+knee)
                h=abs(f*(p.femur*math.cos(a)+p.tibia*math.cos(b))/1000)
                k=abs(f*p.tibia*math.cos(b)/1000)
                cases.append({"hip_deg":hip,"knee_deg":knee,"hip_static_Nm":round(h,3),
                              "knee_static_Nm":round(k,3),
                              "knee_with_2p5_load_factor_Nm":round(k*2.5,3)})
        result[str(contacts)]={"load_each_N":round(f,3),
                  "maximum_hip_Nm":max(x["hip_static_Nm"] for x in cases),
                  "maximum_knee_Nm":max(x["knee_static_Nm"] for x in cases),
                  "maximum_factor_2p5_knee_Nm":max(x["knee_with_2p5_load_factor_Nm"] for x in cases),
                  "cases":cases}
    return result

def export_outline_dxf(span,p,outpath):
    import ezdxf
    doc=ezdxf.new("R2013");doc.header["$INSUNITS"]=4
    for layer in ("OUTER_DRAFT","SLOTS_DRAFT","SPACER_HOLES_DRAFT","NOT_FOR_CNC_RELEASE"):
        doc.layers.new(layer)
    ms=doc.modelspace()
    ms.add_lwpolyline(outer_vertices(span,p),close=True,dxfattribs={"layer":"OUTER_DRAFT"})
    r=p.window_width/2
    for frac in (.4,.6):
        length=span*.12;xl=span*frac-(length-p.window_width)/2
        xr=span*frac+(length-p.window_width)/2
        for yy in (-r,r):
            ms.add_line((xl,yy),(xr,yy),dxfattribs={"layer":"SLOTS_DRAFT"})
        ms.add_arc((xr,0),r,-90,90,dxfattribs={"layer":"SLOTS_DRAFT"})
        ms.add_arc((xl,0),r,90,270,dxfattribs={"layer":"SLOTS_DRAFT"})
    for frac in (.27,.73):
        ms.add_circle((span*frac,0),p.spacer_hole_diameter/2,
                      dxfattribs={"layer":"SPACER_HOLES_DRAFT"})
    ms.add_text("CONCEPT ONLY - NOT FOR CNC",
                dxfattribs={"layer":"NOT_FOR_CNC_RELEASE","height":4,"insert":(0,-40)})
    if doc.audit().has_errors:raise RuntimeError("Invalid DXF")
    doc.saveas(str(outpath))

def from_canonical_parameters(path):
    s=json.loads(Path(path).read_text(encoding="utf-8"))
    return LegDesign(coxa=s["coxa"],femur=s["femur"],tibia=s["tibia"],
                     hip_deg=s["hip_pitch_deg"],knee_deg=s["knee_pitch_deg"],
                     assumed_robot_mass_kg=s["assumed_total_mass_kg"],
                     body_underside_z=s["body_center_z"]-s["body_thickness"]/2)

def export(p,out):
    p.validate();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result={"status":"DRAFT_ONLY_NOT_FOR_MANUFACTURE","parameters":asdict(p),
            "parts":{},"mass_hypotheses":mass_estimate(p),
            "vertical_only_torque_sweep":moment_sweep(p),
            "warnings":["OEM mounting hole geometry not integrated","No bearing fit",
                        "No all-pose collision test","No structural FEA","No physical testing",
                        "Nominal motor rated torque 2.5Nm may be exceeded"]}
    for material in ("plywood","aluminum"):
        for name,span in (("FEMUR",p.femur),("TIBIA",p.tibia)):
            sh=plate(span,p,material)
            prefix=name+"_"+material.upper()+"_LONG_REACH_DRAFT"
            step=out/(prefix+".step")
            cq.exporters.export(sh,str(step),exportType="STEP")
            if not cq.importers.importStep(str(step)).val().isValid():raise ValueError("Invalid STEP")
            dxf=out/(prefix+".dxf");export_outline_dxf(span,p,dxf)
            result["parts"][prefix]={"step":step.name,"dxf":dxf.name,"volume_mm3":round(sh.Volume(),3)}
        assembly=make_module(p,material)
        step=out/("LEG_"+material.upper()+"_LONG_REACH_DRAFT.step")
        assembly.save(str(step),exportType="STEP")
        if not cq.importers.importStep(str(step)).val().isValid():raise ValueError("Invalid leg assembly")
        result["parts"][material+"_assembly"]={"step":step.name,"part_count":len(assembly.children)}
    cq.exporters.export(spacer(p),str(out/"SPACER_ENVELOPE_DRAFT.step"),exportType="STEP")
    foot=leg_points(p)[3]
    result["nominal_clearance_mm"]=round(-foot[2]+p.foot_radius+p.body_underside_z,3)
    (out/"LEG_LONG_REACH_AUDIT.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--params",default="cad/parameters.json")
    a.add_argument("--out",default="out")
    args=a.parse_args()
    report=export(from_canonical_parameters(args.params),args.out)
    print(json.dumps({"parts":list(report["parts"]),"nominal_clearance_mm":report["nominal_clearance_mm"],
                      "mass_hypotheses":report["mass_hypotheses"]},indent=2))

"""SPIDER H6 EXOFRAME v0.4 — parametric skeletal leg CONCEPT.

All joint/drive mounting interfaces, fastener fits, structural strength,
fatigue and range-of-motion clearance remain NOT VERIFIED. STEP is not a
manufacturing release. Geometric motor representations are ENVELOPES only.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse, json, math
import cadquery as cq

@dataclass(frozen=True)
class Design:
    coxa: float = 90.0
    femur: float = 135.0
    tibia: float = 160.0
    hip_deg: float = 35.0
    knee_deg: float = 90.0
    ply_t: float = 6.5
    aluminum_t: float = 3.5
    cavity_width: float = 60.0
    actuator_od: float = 53.0
    actuator_depth: float = 45.2
    spacer_od: float = 12.0
    spacer_id: float = 5.5
    foot_r: float = 13.0
    wood_density: float = 680.0
    aluminum_density: float = 2700.0
    assumed_robot_mass: float = 7.506
    body_bottom_z: float = -60.0
    def validate(self):
        if not (80<=self.coxa<=140 and 115<=self.femur<=210 and 135<=self.tibia<=240):
            raise ValueError("Link length outside design envelope")
        if not (4<=self.ply_t<=12 and 2<=self.aluminum_t<=8):
            raise ValueError("Plate thickness outside design envelope")
        if self.cavity_width<=self.actuator_depth+8:raise ValueError("Insufficient actuator cavity")
        if self.spacer_od<=self.spacer_id+2:raise ValueError("Invalid spacer geometry")
        if not (20<=self.hip_deg<=55 and 55<=self.knee_deg<=125):raise ValueError("Pose out of design range")

def outer_path(L):
    return [(-25,0),(-21,16),(-13,29),(0,31),(17,30),(.18*L,26),
            (.32*L,20),(.46*L,18),(.57*L,19),(.70*L,20),(.83*L,24),
            (L-10,24),(L+4,22),(L+18,11),(L+22,0),(L+18,-11),
            (L+6,-23),(L-12,-25),(.83*L,-21),(.69*L,-16),(.53*L,-15),
            (.38*L,-17),(.23*L,-25),(10,-32),(-8,-31),(-20,-21)]

def windows_path(L):
    return [[(L*.205,5),(L*.39,10),(L*.42,-2),(L*.34,-11),(L*.215,-7)],
            [(L*.49,8),(L*.65,11),(L*.69,-2),(L*.55,-9)],
            [(L*.74,7),(L*.86,12),(L*.92,-2),(L*.82,-12),(L*.745,-8)]]

def cheek(L,p,kind="plywood",cutouts=True):
    p.validate()
    t=p.ply_t if kind=="plywood" else p.aluminum_t
    sh=cq.Workplane("XY").polyline(outer_path(L)).close().extrude(t)
    if cutouts:
        for w in windows_path(L):
            sh=sh.cut(cq.Workplane("XY").workplane(offset=-1).polyline(w).close().extrude(t+2))
    for f in (.15,.88):
        sh=sh.cut(cq.Workplane("XY").workplane(offset=-1).center(f*L,0).circle(p.spacer_id/2).extrude(t+2))
    # Nominal polygon corners only; CNC tool-radius compensation not designed.
    result=sh.val()
    if not result.isValid() or len(result.Solids())!=1 or result.Volume()<=0:
        raise ValueError("Invalid cheek solid")
    return result

def spacer(p):
    result=(cq.Workplane("XY").circle(p.spacer_od/2).circle(p.spacer_id/2)
            .extrude(p.cavity_width).val())
    assert result.isValid()
    return result

def places(p):
    a=math.radians(p.hip_deg);b=math.radians(p.hip_deg+p.knee_deg)
    return ((0,0,0),(p.coxa,0,0),
            (p.coxa+p.femur*math.cos(a),0,-p.femur*math.sin(a)),
            (p.coxa+p.femur*math.cos(a)+p.tibia*math.cos(b),0,
             -p.femur*math.sin(a)-p.tibia*math.sin(b)))

def xf(sh,origin,angle):
    return sh.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,1,0),angle).translate(origin)

def rod(L,p,kind):
    t=p.ply_t if kind=="plywood" else p.aluminum_t
    sh=cheek(L,p,kind)
    return [sh.translate((0,0,p.cavity_width/2)),
            sh.translate((0,0,-p.cavity_width/2-t))]

def diagonal_brace(p,L,reverse=False):
    # Spatial tie-tube envelope: not fastener- or buckling-qualified.
    a=cq.Vector(.17*L,8 if not reverse else -8,-p.cavity_width/2)
    b=cq.Vector(.83*L,8 if not reverse else -8,p.cavity_width/2)
    if reverse:a,b=cq.Vector(a.x,a.y,-a.z),cq.Vector(b.x,b.y,-b.z)
    delta=b.sub(a);v=delta.normalized()
    sh=cq.Solid.makeCylinder(3.6,delta.Length,a,v).cut(cq.Solid.makeCylinder(1.9,delta.Length,a,v))
    assert sh.isValid()
    return sh

def motor_envelope(p,center,vertical=False):
    axis=cq.Vector(0,0,1) if vertical else cq.Vector(0,1,0)
    o=cq.Vector(*center)
    body=cq.Solid.makeCylinder(p.actuator_od/2,p.actuator_depth,
        o.sub(axis.multiply(p.actuator_depth/2)),axis)
    cap1=cq.Solid.makeCylinder(27,2.4,o.add(axis.multiply(p.actuator_depth/2)),axis)
    cap2=cq.Solid.makeCylinder(27,2.4,o.sub(axis.multiply(p.actuator_depth/2+2.4)),axis)
    return body,cap1,cap2

COLORS={"plywood":(.75,.54,.32),"aluminum":(.59,.70,.80),"coxa":(.22,.29,.37),
        "accent":(.91,.41,.12),"spacer":(.62,.68,.74),"bolt":(.35,.42,.49),
        "motor":(.14,.17,.20),"motor_rim":(.42,.47,.52),"foot":(.11,.13,.15)}

def components(p,kind="plywood"):
    p.validate()
    if kind not in ("plywood","aluminum"):raise ValueError("Invalid material")
    A,B,C,D=places(p);result=[]
    def add(name,shape,color):
        if not shape.isValid() or shape.Volume()<=0:raise ValueError("Invalid "+name)
        result.append((name,shape,color))
    for i,part in enumerate(rod(p.coxa,p,"aluminum"),1):
        add("COXA_ALUMINUM_RAIL_"+str(i),xf(part,A,0),"coxa")
    for i,f in enumerate((.15,.88),1):
        add("COXA_CROSS_BRACE_"+str(i),
            xf(spacer(p).translate((p.coxa*f,0,-p.cavity_width/2)),A,0),"spacer")
    for label,origin,L,angle in (("FEMUR",B,p.femur,p.hip_deg),
                                 ("TIBIA",C,p.tibia,p.hip_deg+p.knee_deg)):
        for i,part in enumerate(rod(L,p,kind),1):
            add(label+"_SKELETAL_CHEEK_"+str(i),xf(part,origin,angle),kind)
        for i,f in enumerate((.15,.88),1):
            add(label+"_CROSS_BRACE_"+str(i),
                xf(spacer(p).translate((L*f,0,-p.cavity_width/2)),origin,angle),"spacer")
            for side in (-1,1):
                t=p.ply_t if kind=="plywood" else p.aluminum_t
                head=cq.Workplane("XY").polygon(6,9.5).extrude(2.8).val()
                z=p.cavity_width/2+t if side==1 else -(p.cavity_width/2+t+2.8)
                add(label+"_BOLT_ENVELOPE_"+str(i)+"_"+str(side),
                    xf(head.translate((L*f,0,z)),origin,angle),"bolt")
        for j in (False,True):
            add(label+"_DIAGONAL_SPATIAL_BRACE_"+str(int(j)),
                xf(diagonal_brace(p,L,j),origin,angle),"coxa")
        for side in (-1,1):
            t=p.ply_t if kind=="plywood" else p.aluminum_t
            z=p.cavity_width/2+t if side==1 else -(p.cavity_width/2+t+2.4)
            shield=(cq.Workplane("XY").circle(25).circle(9).extrude(2.4).val())
            add(label+"_COSMETIC_ROOT_SHIELD_"+str(side),
                xf(shield.translate((0,0,z)),origin,angle),"accent")
    for label,center,vertical in (("YAW",A,True),("HIP",B,False),("KNEE",C,False)):
        core,r1,r2=motor_envelope(p,center,vertical)
        add(label+"_MOTOR_ENVELOPE",core,"motor")
        add(label+"_CAP_RIM_1",r1,"motor_rim")
        add(label+"_CAP_RIM_2",r2,"motor_rim")
    add("INTERCHANGEABLE_FOOT_ENVELOPE",
        cq.Solid.makeSphere(p.foot_r,cq.Vector(*D)),"foot")
    return result

def renderable_assembly(p,kind):
    a=cq.Assembly(name="SPIDER_EXOFRAME_v04_"+kind.upper()+"_DRAFT")
    for name,sh,color in components(p,kind):
        a.add(sh,name=name,color=cq.Color(*COLORS[color]))
    return a

def basic_load_sweep(p,contacts=3):
    f=p.assumed_robot_mass*9.81/contacts
    hmax=kmax=0.0
    for h in range(20,61,5):
        for k in range(55,131,5):
            a=math.radians(h);b=math.radians(h+k)
            hmax=max(hmax,abs(f*(p.femur*math.cos(a)+p.tibia*math.cos(b))/1000))
            kmax=max(kmax,abs(f*p.tibia*math.cos(b)/1000))
    return {"load_N_per_support":round(f,4),
            "hip_Nm_max_vertical_only":round(hmax,4),
            "knee_Nm_max_vertical_only":round(kmax,4),
            "knee_Nm_max_with_hypothetical_2p5_multiplier":round(2.5*kmax,4),
            "status":"CALCULATED with ASSUMED mass and support share; not hardware tested"}

def load_canonical(path):
    q=json.loads(Path(path).read_text(encoding="utf8"))
    return Design(coxa=q["coxa"],femur=q["femur"],tibia=q["tibia"],
                  hip_deg=q["hip_pitch_deg"],knee_deg=q["knee_pitch_deg"],
                  assumed_robot_mass=q["assumed_total_mass_kg"],
                  body_bottom_z=q["body_center_z"]-q["body_thickness"]/2)

def export(p,out):
    p.validate();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    audit={"design":"EXOFRAME v0.4","status":"DESIGN CONCEPT; NO MANUFACTURING RELEASE",
           "parameters":asdict(p),"loads":basic_load_sweep(p),"parts":{},
           "warnings":["OEM motor mounting not integrated","No bearings or axle detail",
                       "No validated material strength or FEA",
                       "Full pose collision analysis not done",
                       "Decorative joint shields are not structural flanges"]}
    for kind in ("plywood","aluminum"):
        for label,L in (("FEMUR",p.femur),("TIBIA",p.tibia)):
            sh=cheek(L,p,kind)
            name="EXOFRAME_"+label+"_"+kind.upper()+"_CHEEK_DRAFT"
            path=out/(name+".step");cq.exporters.export(sh,str(path),"STEP")
            if not cq.importers.importStep(str(path)).val().isValid():
                raise ValueError("Invalid STEP "+name)
            audit["parts"][name]={"file":path.name,"volume_mm3":round(sh.Volume(),3),
                                  "verified_closed_solid":True}
        a=renderable_assembly(p,kind)
        path=out/("EXOFRAME_LEG_"+kind.upper()+"_v04_DRAFT.step")
        a.save(str(path),exportType="STEP")
        if not cq.importers.importStep(str(path)).val().isValid():
            raise ValueError("Invalid assembly STEP")
        audit["parts"][kind+"_assembly"]={"file":path.name,"component_count":len(a.children)}
    for label,sh in (("COXA_RAIL",cheek(p.coxa,p,"aluminum")),
                     ("CROSS_BRACE",spacer(p))):
        path=out/("EXOFRAME_"+label+"_DRAFT.step")
        cq.exporters.export(sh,str(path),"STEP")
        if not cq.importers.importStep(str(path)).val().isValid():
            raise ValueError("Invalid subcomponent STEP")
        audit["parts"][label]={"file":path.name}
    (out/"EXOFRAME_AUDIT_v04.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return audit

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--params",default="cad/parameters.json")
    a.add_argument("--out",default="out")
    x=a.parse_args()
    report=export(load_canonical(x.params),x.out)
    print(json.dumps({"parts":list(report["parts"]),"loads":report["loads"]},indent=2))

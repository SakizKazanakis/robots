"""SPIDER ROBOT preliminary parametric solid-envelope CAD.

Reference geometry ONLY. Bearings, interfaces, shaft adapters, fasteners,
cable paths, collision clearances, mass and structural loads require verification.
Nothing here is a production design.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
import cadquery as cq

@dataclass(frozen=True)
class Parameters:
    # Millimetres except explicitly marked mass, gravity and contact count.
    body_length: float = 280.0
    body_width: float = 190.0
    body_thickness: float = 40.0
    body_center_z: float = -40.0
    coxa: float = 60.0
    femur: float = 95.0
    tibia: float = 110.0
    hip_pitch_deg: float = 30.0
    knee_pitch_deg: float = 90.0
    splay_deg: float = 20.0
    motor_outer_diameter: float = 53.0
    motor_axial_depth: float = 45.2
    plate_link_width: float = 18.0
    plate_link_thickness: float = 7.0
    foot_radius: float = 13.0
    shoulder_y: float = 97.0
    shoulder_x: float = 105.0
    payload_plate_length: float = 95.0
    payload_plate_width: float = 85.0
    payload_hole_pitch: float = 40.0
    payload_hole_clearance: float = 4.5
    assumed_total_mass_kg: float = 7.506
    contact_legs_loadcase: int = 3
    gravity_m_s2: float = 9.81

def validate(p: Parameters, leg_count: int) -> None:
    assert leg_count in (4, 6), "Only Q4 or H6 supported"
    for key in ("body_length", "body_width", "body_thickness", "coxa", "femur", "tibia",
                "motor_outer_diameter", "motor_axial_depth", "plate_link_width",
                "plate_link_thickness", "foot_radius"):
        assert getattr(p, key) > 0.0, f"Nonpositive parameter: {key}"
    assert abs(p.hip_pitch_deg) <= 80
    assert 0 < p.knee_pitch_deg < 170
    assert p.contact_legs_loadcase > 0
    assert p.payload_hole_pitch + p.payload_hole_clearance < min(p.payload_plate_length, p.payload_plate_width)

def joints(p: Parameters):
    """Leg plane +X outward, +Z up; yaw occurs about global Z."""
    a = math.radians(p.hip_pitch_deg)
    b = math.radians(p.knee_pitch_deg)
    base = cq.Vector(0, 0, 0)
    hip = cq.Vector(p.coxa, 0, 0)
    knee = cq.Vector(p.coxa + p.femur * math.cos(a), 0, -p.femur * math.sin(a))
    foot = cq.Vector(knee.x + p.tibia * math.cos(a+b), 0,
                     knee.z - p.tibia * math.sin(a+b))
    return base, hip, knee, foot

def link_capsule(a: cq.Vector, b: cq.Vector, width: float, thick: float) -> cq.Shape:
    """Rounded plate without bearing seats: visualization/reference only."""
    d = b.sub(a)
    length = d.Length
    assert length > 1
    pitch = math.degrees(math.atan2(-d.z, d.x))
    mid = a.add(b).multiply(0.5)
    box = cq.Workplane("XY").box(length, thick, width).val()
    box = box.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), pitch).translate(mid)
    end1 = cq.Solid.makeCylinder(width/2, thick, cq.Vector(a.x, a.y-thick/2, a.z), cq.Vector(0, 1, 0))
    end2 = cq.Solid.makeCylinder(width/2, thick, cq.Vector(b.x, b.y-thick/2, b.z), cq.Vector(0, 1, 0))
    return box.fuse(end1, end2).clean()

def cylinder_at(point, axis, diameter, depth):
    return cq.Solid.makeCylinder(diameter/2, depth, point.sub(axis.multiply(depth/2)), axis)

def placement(part: cq.Shape, sx: float, sy: float, yaw: float) -> cq.Shape:
    return part.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), yaw).translate(cq.Vector(sx, sy, 0))

def leg_components(p: Parameters):
    base, hip, knee, foot = joints(p)
    od, depth = p.motor_outer_diameter, p.motor_axial_depth
    tangent = cq.Vector(0, 1, 0)
    metal = cq.Color(0.65, 0.65, 0.7)
    link = cq.Color(0.9, 0.62, 0.2)
    return [
        ("yaw_motor_ENVELOPE", cylinder_at(base, cq.Vector(0, 0, 1), od, depth), metal),
        ("coxa_REFERENCE", link_capsule(base, hip, p.plate_link_width, p.plate_link_thickness), link),
        ("hip_motor_ENVELOPE", cylinder_at(hip, tangent, od, depth), metal),
        ("femur_REFERENCE", link_capsule(hip, knee, p.plate_link_width, p.plate_link_thickness), link),
        ("knee_motor_ENVELOPE", cylinder_at(knee, tangent, od, depth), metal),
        ("tibia_REFERENCE", link_capsule(knee, foot, p.plate_link_width, p.plate_link_thickness), link),
        ("foot_ENVELOPE", cq.Solid.makeSphere(p.foot_radius, foot), cq.Color(0.18, 0.23, 0.23))
    ]

def body_components(p: Parameters):
    body = (cq.Workplane("XY").box(p.body_length, p.body_width, p.body_thickness)
            .edges("|Z").fillet(8).translate((0, 0, p.body_center_z)).val())
    pitch = p.payload_hole_pitch / 2
    holes = [(x, y) for x in (-pitch, pitch) for y in (-pitch, pitch)]
    deck = (cq.Workplane("XY").box(p.payload_plate_length, p.payload_plate_width, 5)
            .faces(">Z").workplane().pushPoints(holes).hole(p.payload_hole_clearance)
            .translate((0, 0, 30)).val())
    return [
        ("chassis_PLACEHOLDER", body, cq.Color(0.24, 0.35, 0.44)),
        ("payload_plate_INTERFACE_DRAFT", deck, cq.Color(0.18, 0.48, 0.69))
    ]

def mounting_points(p: Parameters, leg_count: int):
    xs = (-p.shoulder_x, 0.0, p.shoulder_x) if leg_count == 6 else (-p.shoulder_x, p.shoulder_x)
    for side in (-1, 1):
        for x in xs:
            spread = p.splay_deg if x > 0 else (-p.splay_deg if x < 0 else 0)
            yield x, side*p.shoulder_y, side*90.0 - side*spread

def estimate_load(p: Parameters):
    """Vertical-only equal-share J^T F, NOT dynamic actuator qualification."""
    a = math.radians(p.hip_pitch_deg)
    ab = math.radians(p.hip_pitch_deg+p.knee_pitch_deg)
    fz = p.assumed_total_mass_kg*p.gravity_m_s2/p.contact_legs_loadcase
    hip_lever = abs((p.femur*math.cos(a)+p.tibia*math.cos(ab))/1000)
    knee_lever = abs(p.tibia*math.cos(ab)/1000)
    return {
        "support_force_N_each": round(fz,4),
        "hip_static_vertical_only_Nm": round(fz*hip_lever,4),
        "knee_static_vertical_only_Nm": round(fz*knee_lever,4),
        "assumed_contacts": p.contact_legs_loadcase,
        "missing": ["limb mass", "yaw moments", "ground horizontal forces",
                    "impacts", "thermal derating", "torque-control validation"]
    }

def build(p: Parameters, legs: int, dest: Path):
    validate(p, legs)
    dest.mkdir(parents=True, exist_ok=True)
    arch = "H6" if legs == 6 else "Q4"
    assembly = cq.Assembly(name=f"SPIDER_{arch}_CONCEPT_V0_1")
    for name, shape, color in body_components(p):
        assert shape.isValid() and shape.Volume() > 0
        assembly.add(shape, name=name, color=color)
    modules = leg_components(p)
    feet = []
    for i, (sx, sy, yaw) in enumerate(mounting_points(p, legs), 1):
        for name, shape, color in modules:
            part = placement(shape, sx, sy, yaw)
            assert part.isValid() and part.Volume() > 0
            assembly.add(part, name=f"L{i:02d}_{name}", color=color)
        foot = joints(p)[3]
        angle = math.radians(yaw)
        feet.append([round(sx+foot.x*math.cos(angle),3),
                     round(sy+foot.x*math.sin(angle),3), round(foot.z,3)])
    prefix = f"SPIDER_{arch}_concept_v0_1"
    step = dest/(prefix+".step")
    assembly.save(str(step), exportType="STEP")
    assert assembly.toCompound().isValid()
    imported = cq.importers.importStep(str(step)).val()
    assert imported.isValid() and imported.Volume() > 0
    bb = imported.BoundingBox()
    ground = min(pt[2] for pt in feet)-p.foot_radius
    audit = {
        "status": "CONCEPT_GEOMETRY_ONLY_NOT_MANUFACTURING_RELEASE",
        "cad_engine": "CadQuery / OpenCascade", "architecture": arch,
        "leg_count": legs, "dof_per_leg": 3, "envelope_motor_count": legs*3,
        "assumed_parameters_mm": asdict(p), "geometry_file": step.name,
        "step_import_valid": True,
        "bounding_box_mm": {"x":round(bb.xlen,3), "y":round(bb.ylen,3), "z":round(bb.zlen,3)},
        "nominal_foot_centres_mm": feet,
        "foot_centre_spread_z_mm": round(max(pt[2] for pt in feet)-min(pt[2] for pt in feet),6),
        "nominal_ground_z_mm": round(ground,3),
        "nominal_body_clearance_mm": round(p.body_center_z-p.body_thickness/2-ground,3),
        "estimated_vertical_load_only": estimate_load(p),
        "known_blockers": ["OEM motor STEP fit", "bearing mounts", "shaft adapters",
                           "structural FEA", "collision checks", "wiring", "thermal qualification"]
    }
    (dest/(prefix+"_audit.json")).write_text(json.dumps(audit, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"file":str(step), "valid":True, "bbox_mm":audit["bounding_box_mm"],
                      "load_Nm":audit["estimated_vertical_load_only"]}, ensure_ascii=False))
    return audit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture", choices=("H6","Q4","both"), default="both")
    parser.add_argument("--out", default="out")
    parser.add_argument("--params")
    args = parser.parse_args()
    values = asdict(Parameters())
    if args.params:
        custom = json.loads(Path(args.params).read_text(encoding="utf-8"))
        unknown = set(custom)-set(values)
        if unknown:
            parser.error("Unknown params: "+repr(sorted(unknown)))
        values.update(custom)
    params = Parameters(**values)
    archs = [4,6] if args.architecture=="both" else [6 if args.architecture=="H6" else 4]
    for number in archs:
        build(params,number,Path(args.out))

if __name__=="__main__":
    main()

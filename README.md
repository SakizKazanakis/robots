# SPIDER ROBOT — parametric CAD development

**Current milestone:** CAD-00 — reproducible preliminary 4/6-leg solid-envelope geometry (**NOT FOR MANUFACTURE**).

This project develops a modular sensor-carrying walking inspection robot. The mechanical baseline is an H6 hexapod with three active DOF per leg; Q4 is retained as a comparable reference using the same leg module.

## Workflow

- Parametric modeling engine: **CadQuery 2.8.0 / OpenCascade** (scripted editable parameters in `cad/parameters.json`).
- CAD GUI: **FreeCAD 1.1.4 stable**, for STEP inspection and future native mechanical detail. Imported STEP is NOT a native FreeCAD feature history.
- Blender: visualization only, not the manufacturing source.
- Electronic design: KiCad (future phase).
- Contact/dynamics simulation: MuJoCo or Gazebo (future phase).

### Build

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python cad/spider_cad.py --architecture both --params cad/parameters.json --out out
```

`out/` contains generated STEP for H6 and Q4 plus JSON geometry audits. Artifacts can be regenerated; generated binaries are excluded from Git.

### Preliminary parameters — not validated

- Body envelope: 280 × 190 × 40 mm; relative to shoulder frame its center is 40 mm below the hip plane.
- Limb center distances: coxa 60 mm, femur 95 mm, tibia 110 mm.
- Reference posture: hip pitch 30°, knee pitch 90°.
- Payload draft interface: four nominal Ø4.5 mm holes on a 40 × 40 mm square.
- **Motor CAD is ONLY a cylinder envelope** Ø53 × 45.2 mm; the specific CubeMars AK45-10 V3.0 mounting geometry must be sourced from the OEM STEP before any machining.
- Assumed example mass 7.506 kg; NOT computed from the model or validated.

**Outstanding gates:** vendor motor STEP; bearing supports; shaft connections; bolt patterns; cable paths; self-collision; COM and masses; complete Jacobian and load cases; FEA; single-leg bench testing. Passing a STEP import test does not prove that a physical robot will work.

Sources: [CubeMars](https://www.cubemars.com/product/ak45-10-v3-0-kv75-robotic-actuator.html) · [FreeCAD releases](https://github.com/FreeCAD/FreeCAD/releases) · [CadQuery](https://cadquery.readthedocs.io/).

## Licensing

Original files are provided under MIT (see LICENSE); no third-party manufacturer geometry is redistributed.
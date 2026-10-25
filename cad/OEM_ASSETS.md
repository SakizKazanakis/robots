# CAD source-of-truth and OEM interface evidence

## CubeMars AK45-10 V3.0 KV75

Official OEM support index: https://www.cubemars.com/technical-support-and-software-download.html

Direct 3D drawing archive (listed by manufacturer as STEP/ZIP for **AK45-10 V3.0**, dated 2026-07-29):

https://www.cubemars.com/data/cms/202607/ak45-10-v3-0-kv75-3d-drawing.zip

Official product, dimensions and performance:

https://www.cubemars.com/product/ak45-10-v3-0-kv75-robotic-actuator.html

- Overall product envelope published as Ø53 × 45.2 mm (the reference CAD script approximates it as a cylinder).
- Joint mounting flange, bearings, mechanical output shaft geometry, rear flange, cable exits and fasteners **have not yet been inspected from the OEM STEP**.
- Direct STEP archive is linked but **not included in this repository**. Redistribution rights are not presumed.
- DO NOT assume the similarly named earlier AK45-10 model has matching CAD interfaces.

## Next mechanical gate

1. Obtain and verify OEM archive: SKU, version, units, extracted STEP properties, and reference orientation.
2. Place vendor BREP on three robot joint frames (yaw/pitch/pitch) and verify no collisions.
3. Define mounting adapter plates, output-support bearings, fasteners, cable bends and mechanical limits.
4. Generate native assembly and mechanical drawings; validate center-of-mass and link mass.
5. Model full load cases and complete torque/thermal limits.

**Evidence:** this project has passed parametric geometry generation and STEP re-import only. Not a vendor fit, assembly, FEA, production drawing, or physical validation.

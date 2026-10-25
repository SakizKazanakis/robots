# CAD engineering verification — SPIDER ROBOT

Initial repository main SHA: 2c70cfb553ccec55d668284fa7c8cbac63f90719. Two pre-change GitHub CI runs passed.

## OEM actuator
Official CubeMars AK45-10 V3.0 KV75 STEP archive downloaded on authorized hp_elitebook, not VPS.
ZIP contains `AK45-10 V3.0 KV75.STEP` (1,431,005 bytes).
ZIP SHA-256: `7639AD40ACC1C2D14217E7DD48F71AE9476EA2F1FEC35298D0C3138652126E95`.
**Actual mounting dimensions, axis origins, flanges, bearings and cables NOT YET VERIFIED.** OEM STEP not redistributed.

## Exploratory CAD reference
- Femur length 95 mm, tibia 110 mm; conceptual plywood 6.5 mm and aluminum 3 mm.
- Plate height 34 mm, relief openings *assumed*, no FEA or material qualification.
- Chassis open tray 280 × 190 × 40 mm; assumed wall 5 mm, no mounting fit.
- Payload mounting draft 95 × 85 × 5 mm, pitch 40 mm, clearance 4.5 mm.
- STEP BREP validation does NOT prove load capacity, self-collision clearance or CNC readiness.
- Assumed dimensions must not be interpreted as OEM specifications.

## Stage gates
CAD-00 audit VERIFIED.
CAD-01 source OEM archive RETRIEVED, dimensional examination PENDING.
CAD-02 material qualification NOT VERIFIED.
CAD-03 existing analytical kinematics; dynamic model NOT COMPLETE.
CAD-04/05 preliminary link concepts; metal bearing interfaces NOT COMPLETE.
CAD-06 FEA NOT RUN.
CAD-07 preliminary chassis reference; mount interfaces NOT COMPLETE.
CAD-08 complete solid assembly NOT COMPLETE.
CAD-09 production drawings NOT RELEASED.
CAD-10 geometry code tested locally; GitHub CI result must be verified after upload.

No physical hardware testing performed.

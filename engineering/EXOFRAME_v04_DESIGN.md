# SPIDER H6 / EXOFRAME v0.4 — geometric redesign

**Stage:** CONCEPT CAD; NOT READY FOR MACHINING. This replaces the primitive visual expression of the previous long-reach legs, NOT validated mechanical interfaces.

Source: `cad/legs/exoframe_v04.py`. Shared H6/Q4 center distances and pose are read from `cad/parameters.json`. Previous iterations retained as history.

## Implemented in actual parametric BREP

- Faceted swept dorsal and ventral silhouette, 3 independent shaped apertures per load-bearing plate.
- Two separate outer cheeks per link in 6.5 mm conceptual birch plywood, alternative 3.5 mm conceptual aluminium plate.
- Coxa 90 mm, Femur 135 mm, Tibia 160 mm (center distances).
- Conceptual 60 mm open internal cavity; concept tubular spreaders and four diagonal cross-bay tie sleeves.
- Separate serviceable-bolt **ENVELOPES**, joint decorative caps and 3 motor **ENVELOPES**, no proprietary mounting hole pattern invented.
- Independent colored CadQuery assemblies for plywood and aluminum; separate STEP solids for each link, Coxa and spacer; automatic STEP re-import and geometry tests.

## NOT IMPLEMENTED or VERIFIED

- OEM CubeMars STEP interface extraction and shaft details; bearings, retaining elements and fastening patterns.
- Torsional shear/lateral strut fatigue/functional fasteners.
- CNC cutter relief radii or panel grain direction design.
- Articulation over full angular range; actual robot mass, COM, FEA and measured motor loading.
- A valid verified torque design for 2.5 Nm rated / 7 Nm peak AK45-10 V3.0 actuator. A simple 3-contact vertical-only model predicts static demands beyond nominal and multiplier demands beyond peak.

CAD tests establish volume/solid validity, actual face topology and reproducible STEP export, **not** structural adequacy. Because the exterior is now highly perforated, FEA and physical sheet-material testing are essential before any load rating.

**This new shape is a design candidate, not a released physical robot component.**

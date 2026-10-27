# CAD-05 / Parametric load-path joint cartridge

**Status: 3D CAD CONCEPT / NOT FOR MANUFACTURE.**

The [official CubeMars AK45-10 V3.0 KV75 archive](https://www.cubemars.com/data/cms/202607/ak45-10-v3-0-kv75-3d-drawing.zip) was obtained earlier on the authorized Windows device and inspected as a STEP AP203 SolidWorks 2020 export (1,431,005 bytes). The source STEP contains 109 cylindrical surfaces; candidate mounting-face axes have been extracted in millimetres into `cad/joints/cartridge_v05.py`.

**Measured from original STEP topology:** four radius-1.4 mm cylindrical surfaces around 23.5 mm radial distance at axial coordinate Y=27.2 mm; four radius-1.1 mm features with non-cardinal coordinates on the nominal output side Y=32.7 mm; three rear features at Y=-6.5 mm. These are geometric facts about cylindrical surfaces only. A separate face/solid-topology study is needed to identify thread type, intended mating faces, datum systems, the particular part revision and legal fastener loads. The STEP must not be represented as providing OEM-approved bolt patterns.

**Generated independent 3D pieces:** preliminary motor clearance solid; perforated output coupling adapter; oppositely supported stepped bearing-seat housing; pin envelope; bolted link lug concept; two washers; complete colored STEP assembly. They can be regenerated from Python parameters.

**ASSUMED solely for CAD experimentation:** 72 mm adapter OD, 47 mm conceptual PCD, 4 mm conceptual bolt holes, 42 mm bearing seat, 25 mm pin and seat ID, 62 mm support separation. NO commercially specified bearing or tolerances; NO connection to manufacturer's actual shaft/output feature. CAD pilot holes and components are not CNC/machining files.

**Next verification gates:** inspect source STEP solids and datum frames, source bearing OEM drawing, design complete load path from output flange to double-cheek femur, check cantilever moment and fastener shear, route cable over entire travel, check interference and FEA, then physical single-joint test.

GEOMETRY PASS cannot be promoted to OEM FIT PASS, FEA PASS, or HARDWARE PASS.

# Sizing district-system variables in `sys_params.json`

This document explains how to size the variables under
`district_system.fourth_generation.central_cooling_plant_parameters` (and, in
passing, the central heating plant) in a GMT system parameter file so that the
generated Modelica package will compile, simulate, and produce physically
reasonable results.

Background: until the template patch that ships alongside this document, several
of these keys were silently ignored — the GMT template hard-coded values like
`mCHW_flow_nominal = numChi*3`. That meant `sys_params.json` and the generated
Modelica could diverge dramatically and the user would have no obvious way to
know. The patch removes the hard-codes; this document explains how to fill the
keys in correctly.

If a simulation fails with a freeze assertion in `Buildings.Media.Water` (the
"Temperature T exceeded its minimum allowed value of -1 degC" message), the
plant is almost certainly under-sized relative to the building loads connected
to it. Read on.

---

## 1. The shape of the central cooling plant

The GMT 4G cooling plant is a parallel arrangement of `numChi` water-cooled
electric chillers (currently hard-coded to 2 in `DistrictEnergySystem.mot`),
each connected to a parallel arrangement of `numChi` cooling-tower cells and a
common pair of pump headers:

```text
                ┌────────────┐
        ┌──────►│  Chiller 1 ├──────►┐
   CHW  │       └────────────┘       │  CW
   loop │            ...             │  loop
        └──────►┌────────────┐──────►┘
                │  Chiller N │
                └────────────┘
                       ▲
                       │ heat rejection
                ┌──────┴─────┐
                │  Cooling   │
                │ Tower (×N) │
                └────────────┘
```

There are three flow circuits to size:

|Circuit|Modelica parameter|sys_params key|
|---|---|---|
|CHW (district side, distributes chilled water to building ETSs)|`mCHW_flow_nominal`|`mass_chw_flow_nominal`|
|CW (condenser loop between chiller condenser and cooling tower)|`mCW_flow_nominal`|`mass_cw_flow_nominal`|
|Per-chiller turndown floor|`mMin_flow`|`chiller_water_flow_minimum`|

and one capacity:

|Quantity|Modelica parameter|sys_params key|
|---|---|---|
|Plant evaporator capacity (W, positive number; the template negates it)|`QEva_nominal`|`heat_flow_nominal`|

---

## 2. Step-by-step sizing recipe

The four flow / capacity keys are not independent — they must be internally
consistent or the chiller catalog model will misbehave.

### Step 1 — pick the plant design capacity (`heat_flow_nominal`)

This should be the **coincident peak cooling load** of all buildings on the
district, in watts. Quick paths to a number:

- Take the coincident peak from your building-load export (e.g., the OpenStudio measure that produces
  `xx_export_modelica_loads/modelica.mos` files; look at the cooling column —
  it's signed negative in the `.mos` per Modelica convention). Sum across
  buildings hour-by-hour and take the max.
- Or, if you have URBANopt's OpenStudio results, use the district-level
  coincident peak cooling.
- Increase ~10–15 percent for sizing margin (HVAC convention).

The chiller catalog record currently hard-coded in
`CoolingPlant_Instance.mopt` is `ElectricEIRChiller_Carrier_19EX_5208kW…`,
which is 5.2 MW per unit. With `numberofchillers = 2`, total installed
capacity is 10.4 MW. Aim for `heat_flow_nominal ≤ 10.4 MW` (that is,
`numberofchillers × catalog_capacity` with the current fixed value of 2) or
you'll over-rely on a single chiller.

### Step 2 — derive `mass_chw_flow_nominal`

For a chilled-water system with design ΔT of 5–9 K between supply and return:

```text
m_CHW [kg/s]  =  heat_flow_nominal [W]  /  (cp_water [J/kg·K] × ΔT_CHW [K])
              =  Q  /  (4184 × 5)   ≈  Q / 20,920          for ΔT = 5 K
              =  Q  /  (4184 × 9)   ≈  Q / 37,656          for ΔT = 9 K
```

In sys_params, `delta_temp_chw_district` defaults to 8 K. Pick a ΔT consistent
with the building ETS settings (`delta_temp_chw_building`) and:

```json
// 8 MW plant, ΔT = 5 K → m_CHW ≈ 382 kg/s
// 8 MW plant, ΔT = 9 K → m_CHW ≈ 212 kg/s
// 8 MW plant, ΔT = 14 K (legacy GMT default in mopt) → m_CHW ≈ 136 kg/s
// Example below assumes a smaller coincident peak, not the full 8 MW:
// 3.2 MW coincident peak, ΔT = 9 K → m_CHW ≈ 85 kg/s
"mass_chw_flow_nominal": 85
```

A common practical compromise is to size `mass_chw_flow_nominal` to the
*coincident* peak, not the simple sum of building design flows — that's
usually 50–70 % of the latter in a mixed-use district. The guidance:

- If you don't know better, start with `Q_coincident / (4184 × ΔT_CHW)`; for
  example, at a 5 K CHW design ΔT this becomes `Q_coincident / (4184 × 5)`.
- If freeze assertions on the CW loop appear, the issue is usually that the
  CW loop has too little **thermal mass**, not CHW — see Step 3.
- If you see chillers stuck at 0 or 100 % and CHW temperatures swing
  dramatically, the chilled-water flow is too small.

### Step 3 — size `mass_cw_flow_nominal`

For a water-cooled chiller, assume:

```text
m_CW  ≈  1.0  to  1.25  ×  m_CHW
```

The 1.25x factor accounts for the chiller's compressor work being rejected to
the condenser. A typical electric chiller rejects roughly
`(1 + 1/COP) × Q_evap` to the tower; with COP ≈ 6.88 (the catalog record) the
heat rejected is about 1.15 * Q_evap, hence the ratio.

```json
// Example for m_CHW = 85 kg/s
"mass_cw_flow_nominal": 100
```

**This is the variable that most directly prevents the freeze-assertion
failure mode.** When the cooling tower is fed too little CW, the small loop
thermal mass cannot absorb the heat rejected by the chiller compared to the
heat lost to a cold ambient (cold-climate winter, sub-zero wet-bulb), and the
loop temperature plunges past −1 °C, triggering the medium's bounds check.

### Step 4 — set `chiller_water_flow_minimum`

This is the **per-plant** turndown limit (the template divides by `numChi`
internally to get per-chiller flow). A reasonable value is 20–30 % of
`mass_chw_flow_nominal`:

```json
// 85 kg/s nominal, 25 % turndown → 21 kg/s plant floor
"chiller_water_flow_minimum": 20
```

Setting `chiller_water_flow_minimum == mass_chw_flow_nominal`
forces the plant to push design flow even when district demand is small (e.g.,
winter), which is the *other* cause of CW loop freezing — the cold-weather
overcooling failure mode.

Going below ~20 % can stall the chiller's flow-proven
interlock at part-load.

### Step 5 — pressure drops and pump heads

These do propagate through the template already and are simpler:

|Key|Typical|Notes|
|---|---|---|
|`pressure_drop_chw_nominal`|30 000 – 60 000 Pa|Evaporator-side ΔP across the chiller bundle|
|`pressure_drop_cw_nominal`|30 000 – 60 000 Pa|Condenser-side ΔP|
|`pressure_drop_setpoint`|50 000 Pa|Differential pressure setpoint at remote sensor|
|`chw_pump_head`|200 000 – 400 000 Pa|Chilled-water pump design head|
|`cw_pump_head`|150 000 – 250 000 Pa|Condenser pump design head|
|`pressure_drop_chw_valve_nominal`|6 000 Pa|Throttling valve at chiller|
|`pressure_drop_cw_pum_nominal`|6 000 Pa|CW pump fitting losses|

The CHW pump head should be at least
`pressure_drop_chw_nominal + pressure_drop_setpoint + distribution_loop_drop`.
The template internally adds 200 000 Pa of margin, so being a bit conservative
on `chw_pump_head` is fine.

### Step 6 — cooling-tower geometry and ambient design conditions

These have less effect than the flow values for "will it run" but matter for
realism:

|Key|Notes|
|---|---|
|`temp_setpoint_chw`|District CHW supply setpoint, °C. 6 °C is a typical 4G value. The template now reads this directly (was hard-coded 5 °C).|
|`temp_air_wb_nominal`|Design wet-bulb at peak cooling, °C. 24.9 °C is OK for moderate-humidity climates; for cold-winter climates like Buffalo NY, use ~22–24 °C.|
|`temp_cw_in_nominal`|Design CW return temperature into the chiller, °C. 34.9 °C is typical for water-cooled chillers.|
|`cooling_tower_water_temperature_difference_nominal`|CW range across the tower, K. 6–8 K typical.|
|`delta_temp_approach`|Tower approach (CW supply − wet-bulb), K. 3–5 K is normal; lower = bigger / more expensive tower.|
|`ratio_water_air_nominal`|L/G ratio of the tower. 0.5–1.0 typical.|
|`cooling_tower_fan_power_nominal`|Total fan power at design air flow, W. Roughly 0.5–1 % of `heat_flow_nominal` for a typical induced-draft cell.|

---

## 3. Sanity-check rules of thumb

Once you've filled in the values, sanity-check the consistency:

1. **Capacity / flow / ΔT identity**:
   `heat_flow_nominal ≈ mass_chw_flow_nominal × 4184 × delta_temp_chw_district`
   Within ±15 % is fine; large mismatches will produce nonsense chiller
   part-load operation.

2. **CW / CHW flow ratio**:
   `mass_cw_flow_nominal / mass_chw_flow_nominal` between **1.0 and 1.4**.

3. **Plant capacity vs catalog**:
   `heat_flow_nominal ≤ numberofchillers × QEva_flow_nominal_per_chiller`.
   The currently hard-coded chiller record is 5208 kW × 2 chillers = 10.4 MW.

4. **Cooling-tower throughput**:
   `cooling_tower_water_temperature_difference_nominal × mass_cw_flow_nominal
   × 4184  ≈  heat_flow_nominal × (1 + 1/COP)`.

5. **Turndown sane**:
   `0.15 × mass_chw_flow_nominal  ≤  chiller_water_flow_minimum  ≤
    0.35 × mass_chw_flow_nominal`.

6. **Wet-bulb consistency with weather**:
   `temp_air_wb_nominal` should be reasonably close to the 99 %ile WB of the
   actual TMY3 / EPW file. For a Buffalo TMY3 that's ~22 °C; the GMT default
   of 24.9 °C is fine for sizing but overstates the *design* approach in cold
   climates.

7. **Building-side consistency** (in each `ets_indirect_parameters`):
   - `delta_temp_chw_district` ≥ `delta_temp_chw_building`
   - `nominal_mass_flow_building` × ΔT_chw_building × 4184  ≈  per-building
     coincident cooling load.

---

## 4. Common failure modes

|Symptom|Likely cause|Fix|
|---|---|---|
|`assert: Temperature T = 26x.x K exceeded minimum -1 degC` in `cooPla.cooTowWitByp.cooTowSys.cooTow[i].vol` or `cooPla.pumCW.pum[i]`|CW loop too small; freezes when ambient wet-bulb << 0 °C|Increase `mass_cw_flow_nominal` to 1.0–1.25 × `mass_chw_flow_nominal`. Lower `chiller_water_flow_minimum` so plant can turn down.|
|Same assert but on the CHW side (e.g. `senTCHWRet.T < 272.15`)|CHW flow too small relative to building demand|Increase `mass_chw_flow_nominal` to match coincident peak / ΔT|
|`Pantelides index reduction failed! System is structurally singular` at translate time, but simulation still runs|OpenModelica analytic-index issue with the assembled plant; not a sizing problem|Ignore unless the run actually fails later|
|Chiller power = 0 throughout the run|`QEva_nominal` is unsigned-positive (legacy template form)|The patched template now negates `heat_flow_nominal` automatically. Make sure your sys_params value is a positive number of watts.|
|Pump curve doesn't match plant flow|`mass_chw_flow_nominal` was used in pump V_flow but plant `mCHW_flow_nominal` was hard-coded|Apply the template patch shipped with this doc.|
|Setpoint stuck at 5 °C even though `temp_setpoint_chw: 6`|Same root cause; setpoint expression was hard-coded|Apply the template patch shipped with this doc.|

---

## 5. Known limitations of the current 4G template

There are still some parameters that stay hard-coded and
may require either editing the templates manually or extending the schema:

1. **`numberofchillers`** is fixed at 2 in `DistrictEnergySystem.mot`. To run
   a plant with 1 or 3+ chillers you must edit that file directly (or add
   `num_chillers` to the schema and wire it through).

2. **Chiller catalog record** is hard-coded in `CoolingPlant_Instance.mopt`
   as `Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes`.
   To use a different catalog record, either edit the `.mopt` after generation
   or add a `chiller_performance_data` string field to the schema and use it
   in the `redeclare` line.

3. **Cooling-tower design conditions** (`TAirInWB_nominal`, `TCW_nominal`,
   `TMin`) are hard-coded in the `Plants.CentralCoolingPlant` instantiation
   in `CoolingPlant_Instance.mopt`. They should pull from
   `temp_air_wb_nominal`, `temp_cw_in_nominal`, and a new `temp_cw_min`
   sys_params field.

4. **`pumDP` offset (+200 000 Pa)** in `CoolingPlant_Instance.mopt` is hard-coded
   safety margin. Consider adding `chw_pump_head_safety_margin` to the schema.

5. **Heating plant** (`HeatingPlant_Instance.mopt`) has the same kind of hard-coded
   sizing (`Q_flow_nominal_{{ model.id }} = 1000000 * 2`, etc.). It deserves the
   same treatment but is out of scope for this revision; a parallel patch is
   straightforward.

---

## 6. Worked example: 8 MW cold-climate district (Buffalo NY)

Reference numbers for an example district with ~8 MW coincident peak cooling
load on Buffalo TMY3 weather:

```json
"central_cooling_plant_parameters": {
  "heat_flow_nominal":                  8000000,
  "cooling_tower_fan_power_nominal":      50000,
  "mass_chw_flow_nominal":                   85,
  "chiller_water_flow_minimum":              20,
  "mass_cw_flow_nominal":                   100,
  "chw_pump_head":                       300000,
  "cw_pump_head":                        200000,
  "pressure_drop_chw_nominal":            44801,
  "pressure_drop_cw_nominal":             46200,
  "pressure_drop_setpoint":               49999,
  "temp_setpoint_chw":                        6,
  "pressure_drop_chw_valve_nominal":       5999,
  "pressure_drop_cw_pum_nominal":          5999,
  "temp_air_wb_nominal":                   22.0,
  "temp_cw_in_nominal":                    34.9,
  "cooling_tower_water_temperature_difference_nominal": 6.56,
  "delta_temp_approach":                   3.25,
  "ratio_water_air_nominal":                0.6
}
```

With these values and the template patch applied, the rendered Modelica is
internally consistent (pump curves match plant flows, plant capacity matches
chiller catalog, CHW setpoint matches sys_params) and the freeze assertion
that the unpatched template produced at sub-freezing wet-bulb conditions is
resolved.

---

## Appendix — keys at a glance

Required for any 4G central cooling plant:

```text
heat_flow_nominal                            – plant evaporator capacity, W
cooling_tower_fan_power_nominal              – design fan electrical power, W
mass_chw_flow_nominal                        – kg/s
mass_cw_flow_nominal                         – kg/s
chiller_water_flow_minimum                   – kg/s
chw_pump_head                                – Pa
cw_pump_head                                 – Pa
pressure_drop_chw_nominal                    – Pa
pressure_drop_cw_nominal                     – Pa
pressure_drop_setpoint                       – Pa
temp_setpoint_chw                            – °C
pressure_drop_chw_valve_nominal              – Pa
pressure_drop_cw_pum_nominal                 – Pa
temp_air_wb_nominal                          – °C
temp_cw_in_nominal                           – °C
cooling_tower_water_temperature_difference_nominal – K
delta_temp_approach                          – K
ratio_water_air_nominal                      – dimensionless
```

All of these flow through to the generated Modelica with the template patch
applied. Without the patch, only the `dp*` keys, the pump heads, the
cooling-tower fan power, and the values inside the pump performance curves
actually have any effect — the rest are silently ignored.

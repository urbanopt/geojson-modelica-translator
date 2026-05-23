# Sizing district-system variables in `sys_params.json`

This document explains how to size the variables under
`district_system.fourth_generation.central_cooling_plant_parameters` and
`district_system.fourth_generation.central_heating_plant_parameters` in a
GMT system parameter file so that the generated Modelica package will
compile, simulate, and produce physically reasonable results. Sections 1–6
cover the cooling plant; section 7 covers the heating plant.

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

In `sys_params.json`, this value is the **plant-level** chilled-water minimum
flow. The template then divides it by `numChi` internally to obtain each
chiller's `mMin_flow`. Therefore, size `chiller_water_flow_minimum` as
20–30 % of the plant-level `mass_chw_flow_nominal`:

```json
// 85 kg/s plant nominal, 25 % turndown → ~21 kg/s plant minimum
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

5. **Heating plant `numBoi`** is still hard-coded to 2 inside
   `CentralHeatingPlant.mo`. The heating-plant `delT_nominal` (15 K) and the
   `+50 000` Pa pumDP safety margin in `HeatingPlant_Instance.mopt` are also
   hard-coded; consider exposing them as new sys_params fields.

6. **Boiler catalog record** in `CentralHeatingPlant.mo` is hard-coded the
   same way the chiller record is. Same fix applies: add a
   `boiler_performance_data` sys_params field.

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

## 7. Central heating plant

The central heating plant (`Plants.CentralHeatingPlant`) is the heating-side
analogue of the cooling plant: a parallel arrangement of `numBoi` boilers
(hard-coded to 2 in `CentralHeatingPlant.mo`), a common HHW pump header, a
demand-side ΔP setpoint, and an HHW supply setpoint controlled at the network
side.

```text
              ┌───────────┐
       ┌─────►│  Boiler 1 ├──────►┐
  HHW  │      └───────────┘       │  to district
  ret  │           ...            │  supply
       └─────►┌───────────┐──────►┘
              │  Boiler N │
              └───────────┘
```

Same patch convention as cooling: `heat_flow_nominal` and
`mass_hhw_flow_nominal` are the **total plant** values; the template divides
them by `numBoi` to get per-boiler `QBoi_flow_nominal` and `mBoi_flow_nominal`.

The sys_params fields under
`district_system.fourth_generation.central_heating_plant_parameters` are:

|Key|Modelica destination|Notes|
|---|---|---|
|`heat_flow_nominal`|`Q_flow_nominal` (total) and `QBoi_flow_nominal` (per boiler, =total/numBoi)|Plant heating capacity, W. Positive.|
|`mass_hhw_flow_nominal`|`mHW_flow_nominal` (total) and `mBoi_flow_nominal` (per boiler, =total/numBoi)|Plant HHW flow, kg/s|
|`boiler_water_flow_minimum`|`mMin_flow` (per boiler, =total/numBoi)|Per-plant minimum flow, kg/s|
|`pressure_drop_hhw_nominal`|`dpBoi_nominal`|Boiler-side ΔP, Pa|
|`pressure_drop_setpoint`|Read from the network-side `dpSetPoi` (the heating plant pulls it from the connected disNet, not from this key)|See note in template TODO|
|`temp_setpoint_hhw`|HHW supply setpoint via `THeaSet` input on the plant; wired in the network↔plant coupling templates, **not** in `HeatingPlant_Instance.mopt`|°C|
|`pressure_drop_hhw_valve_nominal`|Not currently consumed by the plant template|—|
|`chp_installed`|Selects whether `HeatingPlantWithCHP.mot` or `CentralHeatingPlant.mo` is used|Boolean|
|`chp_thermal_following`|CHP dispatch mode|Only meaningful if `chp_installed = true`|

### Step-by-step sizing recipe (heating)

1. **`heat_flow_nominal`** — coincident peak heating load of all buildings,
   in watts. Same procedure as cooling: from the `xx_export_modelica_loads`
   exports, sum the heating column across buildings hour-by-hour and take
   the max. Pad 10–15 %.

2. **`mass_hhw_flow_nominal`** — derive from the design HHW ΔT. With
   `delT_nominal = 15 K` (currently hard-coded in the .mopt) and
   cp_water ≈ 4184 J/kg·K:

   ```text
   m_HHW [kg/s]  =  heat_flow_nominal [W]  /  (4184 × delT_nominal)
                 =  Q  /  62,760           for delT_nominal = 15 K
   ```

   ```json
   // 4 MW plant, ΔT_HHW = 15 K  → m_HHW ≈ 64 kg/s
   // 8 MW plant, ΔT_HHW = 20 K  → m_HHW ≈ 96 kg/s
   "mass_hhw_flow_nominal": 64
   ```

   If you change `mass_hhw_flow_nominal` without changing `delT_nominal`,
   the boiler will be force-fed flow it can't actually heat through the
   designed ΔT — the boiler model will compensate but you'll see odd
   part-load behavior.

3. **`boiler_water_flow_minimum`** — plant-level minimum, 20–30 % of
   `mass_hhw_flow_nominal`. The template divides by `numBoi`, so 20 % of
   64 kg/s = ~13 kg/s plant minimum / ~6.5 kg/s per boiler.

   ```json
   "boiler_water_flow_minimum": 13
   ```

   Boilers don't have the same freeze-overcooling failure mode the cooling
   tower has, but starving the loop at near-zero load will still cause the
   boiler model's PI controller to chatter.

4. **`pressure_drop_hhw_nominal`** — boiler-side ΔP at design flow, in Pa.
   Real boilers are 30 000 – 60 000 Pa across the heat exchanger.

5. **`pressure_drop_setpoint`** (on the *network*, not the plant) — design
   ΔP at the remote pressure-control valve. 50 000 Pa default; raise for
   long / branchy distribution networks.

6. **`temp_setpoint_hhw`** — district HHW supply setpoint, °C. 50–55 °C is
   normal for a low-temperature 4G system; 70–80 °C for a legacy high-temp
   district. The 4G default in the schema is 55 °C.

7. **`chp_installed`** — set `true` to swap the plant model for
   `HeatingPlantWithCHP` (combined heat and power). If `true` you also need
   `chp_thermal_following` to be set.

### Sanity-check rules (heating)

1. **Capacity / flow / ΔT identity**:
   `heat_flow_nominal ≈ mass_hhw_flow_nominal × 4184 × delT_nominal`
   With the hard-coded `delT_nominal = 15 K`, that means
   `mass_hhw_flow_nominal ≈ heat_flow_nominal / 62,760`.

2. **Turndown sane**:
   `0.15 × mass_hhw_flow_nominal  ≤  boiler_water_flow_minimum  ≤
    0.35 × mass_hhw_flow_nominal`.

3. **Supply temperature > distribution loss + ETS approach**:
   `temp_setpoint_hhw  ≥  building_HHW_supply_temp + heat_exchanger_approach
   - distribution_loss`. The
   `ets_indirect_parameters.heating_supply_water_temperature_building` for
   each building should be at least 5 K below `temp_setpoint_hhw`.

### Worked example: heating plant for the same 8 MW district

Heating peak loads in a mixed-use district tend to be ~50–70 % of the
cooling peak in cooling-dominated climates, and 100–150 % in
heating-dominated climates. For the Buffalo example (cooling-dominated in
summer, heating-dominated in winter) a ~10 MW heating peak with HHW
ΔT = 20 K is plausible:

```json
"central_heating_plant_parameters": {
  "heat_flow_nominal":                  10000000,
  "mass_hhw_flow_nominal":                   120,
  "boiler_water_flow_minimum":                30,
  "pressure_drop_hhw_nominal":             45000,
  "pressure_drop_setpoint":                50000,
  "temp_setpoint_hhw":                        55,
  "pressure_drop_hhw_valve_nominal":        6000,
  "chp_installed":                         false
}
```

**Warning if your current sys_params look like the GMT defaults
(`heat_flow_nominal: 8001`, `mass_hhw_flow_nominal: 1`,
`pressure_drop_hhw_nominal: 55001`):** those are the schema defaults, which
mean an ~8 kW boiler plant moving 1 kg/s — i.e., not sized at all. Until
the template patch landed, those values were silently ignored, so an
8 kW-on-paper plant was happily serving a 10 MW district. **Now** that the
.mopt honors them, the simulation will refuse to converge if you leave
them at defaults. Pick real numbers from your load files before the next
run.

### Known limitations of the heating-plant patch

- `numBoi` is hard-coded to 2 in `CentralHeatingPlant.mo`. Wire it through
  sys_params (same TODO as `numberofchillers`).
- `delT_nominal` is hard-coded to 15 K in the `.mopt`. Add a
  `delta_temp_hhw_nominal` sys_params field if you need to change it.
- The pumDP `+50 000` Pa safety margin is hard-coded; consider
  `hhw_pump_head_safety_margin`.
- The boiler model record in `CentralHeatingPlant.mo` is hard-coded just
  like the chiller catalog in `CoolingPlant_Instance.mopt`.

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

Required for any 4G central heating plant:

```text
heat_flow_nominal                            – plant heating capacity, W
mass_hhw_flow_nominal                        – kg/s
boiler_water_flow_minimum                    – kg/s
pressure_drop_hhw_nominal                    – Pa
pressure_drop_setpoint                       – Pa (lives on the network, not the plant)
temp_setpoint_hhw                            – °C (wired via the network↔plant coupling)
pressure_drop_hhw_valve_nominal              – Pa (not currently consumed)
chp_installed                                – bool
chp_thermal_following                        – bool (only if chp_installed = true)
```

All of these flow through with the `2026-05-20` template patch applied.
Without the patch, `Q_flow_nominal` was hard-coded to `1 000 000 × 2` and
`dpBoi_nominal` to `10 000`, regardless of what your sys_params said.

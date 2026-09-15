# TEA calibration (INTERNAL: supplier documents shared with Frontier)

Two supplier TEAs in the Frontier template (May 2025 version) were added on
2026-09-08. Numbers below are copied from the "Cost inputs" and "LCA inputs"
sheets; they are confidential and must not appear in any published output.
They enter `scripts/constants.py` as `SYSTEM_MODES["reactor_activated"]` and
`TEA_INTERNAL`.

## Arca (Thetford Mines, Bell Mine, Quebec)

| Item | Demo (100 kt/yr feed) | FOAK TRL 9 | NOAK |
|---|---|---|---|
| Gross CDR | 29,727 tCO2/yr | 285,548 | 285,548 |
| Implied uptake | **0.297 tCO2 per t feed** | | |
| Net negativity | 0.960 | 0.965 | 0.965 |
| Electricity | 1.3 MWh/tCO2 at $46/MWh | 0.9 at $40 | 0.7 at $40 |
| Grid | HydroQuebec, 1.2 gCO2/kWh | | |
| Water | 1 t/tCO2 at $2/t | | |
| CapEx incl. financing | $221/tCO2 net | $30 | $25 |
| Fixed opex | $54 | $22 | $11 |
| Energy | $64 | $39 | $31 |
| Other variable (maintenance, feedstock fee $3, MRV $4, IP, asset mgmt) | $99 | $48 | $37 |
| **Total** | **$439/tCO2 net** | **$140** | **$105** |

Process: material handling, comminution (ball mill; HPGR considered), heat
exchangers, microwave mineral activation, "smart churning" with MRV. The
0.30 tCO2/t uptake is only reachable because activation liberates Mg from bulk
serpentine; it is not an ambient-carbonation number.

## Anvil C1 (Nevada; confirmed by Zeke 2026-09-08)

Notes cite the NV grid at 280 gCO2/kWh with 13 g/yr decarbonisation and ore
from "relatively soft contact metamorphic and serpentinite deposits", i.e. a
brucite-bearing contact-metamorphic deposit rather than asbestos tailings.

| Item | C1 (this project) | NOAK (3rd megasite, purpose-mined ore) |
|---|---|---|
| Gross CDR | 42,000 tCO2/yr | 14.17 Mt/yr |
| Feed rate | not given | not given |
| Net negativity | 0.945 | 0.979 |
| Electricity | 0.608 MWh/tCO2 at $120/MWh | 0.786 at $60 (PV+BESS, 15 g/kWh); higher because of lower brucite grade |
| Water | 6.5 t/tCO2 at $0.4/t | 5.4 |
| Bare erected cost | $69.5M ($69/tCO2) | $8.12B ($12/tCO2) |
| CapEx incl. financing | $249/tCO2 net | $54 |
| Fixed opex | $82 | $2 |
| Energy | $77 | $48 |
| Other variable (grinding media $5.6, maintenance 3.5% of capex) | $73 | $29 |
| **Total** | **$482/tCO2 net** | **$134** |

Process: loaders/conveyors, crusher, sorter, comminution and pelletization, air
handling, reactors, final storage. Ore at C1 is assumed 10 years old (no
embodied emissions); NOAK purpose-mines.

## How the model uses them (revised: FOAK / NOAK tiers)

`constants.TIERS` holds, per tier, the gross-basis $/tCO2 for capex, fixed opex
and other variable opex, the electricity intensity (MWh/tCO2) and the TEA
electricity price, each as a (Arca, Anvil) pair; the model draws uniformly
between the pair. FOAK = Arca demo column and Anvil C1 column; NOAK = both NOAK
columns. Uptake per tonne of feed is drawn 0.25-0.297 (Arca 0.297; Anvil feed
rate unknown). Site substitutions: electricity price (HydroQuebec $46/MWh, Nevada
$120, else the tier default range), grid CO2 intensity (net-negativity), and
quarrying plus access cost for greenfield feed.

## Earlier note

- `reactor_activated` mode: activation fraction of bulk serpentine Mg LOW 0.25 /
  CENTRAL 0.55 / HIGH 0.80 (Arca's 0.30 t/t implies ~0.63 of a 0.476 x 0.8
  serpentinite capacity), electricity 200-400 kWh per tonne of feed (Arca 0.7-1.3
  MWh/tCO2 x 0.30), capex $20-120 per tonne of feed, fixed-plus-other opex
  $45-250 per tCO2 spanning NOAK to demo.
- Both TEAs report roughly 4x cost reduction from first project to NOAK; the
  model's LOW/HIGH scenarios bracket that rather than pick a year.
- Anvil's feed throughput is missing, so its uptake per tonne cannot be derived;
  requested in TODO.md.

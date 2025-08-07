Yes, I understand.
In plain words you want a “production-planner” that always looks at the rolls that are waiting for development, estimates the chemistry they would consume, then tells the operator — before any single roll is selected — exactly which set of rolls should go into the next development run so that …
the chemicals in the machine are used up in as few runs as possible (ideally one)
no chemical batch ever ages more than ~14 days once mixed
we keep projects together (don’t split a project across two runs if that can be avoided)
inside a run we process lots of rolls, preferring to fit many small rolls before adding big ones so we don’t exceed tank capacity.
Below is the high-level design I would use.
Data we need
Roll attributes (already available):
id, project_id / project_name
film_type (16 mm / 35 mm) and pages_used → area_m²
can_develop, is_developing, is_completed
Chemical batch attributes (already available):
capacity_m² (how much total area the batch can process)
remaining_capacity_m²
installation_date → age, hours_until_lockout, etc.
Derived values we’ll calculate:
roll_area_m² = pages_used / 100 (cm) × film_width_m (already done in JS for time)
roll_chem_need = roll_area_m² (1 m² of film ≈ 1 m² consumption for every chemical)
total_area_by_project
“fit score” for putting a roll into the plan.
Server-side service: Planning engine
Endpoint: GET /api/development/planner/
Steps executed:
Query all rolls where can_develop = true and is_developing = false and is_completed = false.
Group by project_id → build project buckets.
For each bucket calculate:
total_area
roll_count
smallest_roll_area, largest_roll_area
ready_since (oldest ready date inside the bucket)
Ask current chemical status endpoint for remaining_capacity_m² (developer, fixer, cleaners).
The limiting reagent is the lowest remaining capacity across the four chemicals.
Packing algorithm
5a. Sort project buckets by:
a) ready_since (older projects first)
b) then by total_area (smaller first)
5b. Iterate buckets, add whole bucket if it fits into remaining capacity.
5c. If a bucket is too large, fall back to roll-level packing:
sort its rolls by area ascending
greedily add rolls until adding the next one would overflow capacity.
5d. Stop when we reach 90-95 % of remaining capacity (configurable
head-room so we don’t accidentally exceed).
Compute projection outputs:
projected_area_m², projected_roll_count
projected_processing_time = Σ(film_length_m) (already 1 min per meter rule)
chemical_remaining_after_run = remaining_capacity – projected_area
earliest “best before” date among current chemicals
Return JSON:
{
success: true,
run_plan: {
rolls: [ {id, film_number, project, area_m², …}, … ],
grouped_by_project: [
{project_id, project_name, area_m², roll_count, rolls:[…]},
…
],
totals: { area_m², roll_count, est_time_min },
chemistry: {
capacity_left_m²,
capacity_after_run_m²,
age_warning: boolean,
lockout_at: ISO
},
advice: "OK to start now" | "Wait for more rolls" | "Chemicals expired",
generated_at: ISO
}
}
Planning is pure read-only so it can be done every page load or via WebSocket push when a roll becomes ready.
Front-end changes (develop.html / develop.js)
UI block (new, above “Rolls Ready for Development”):
┌──────────────────────────────────────────────────────┐
│ Development Run Planner (auto-refresh every 30 s) │
├──────────────┬───────────────────────────────────────┤
│ Capacity │ 7.80 m² of 10 m² remaining (22 %) │
│ Age │ Chemicals locked in 36 h (warning) │
├──────────────┴───────────────────────────────────────┤
│ Suggested next run: 4 rolls, 8.5 m², 9 min total │
│ • Project “ACME-INV” – 2 rolls (4.2 m²) │
│ • Project “BETA” – 1 roll (1.3 m²) │
│ • Project “OMEGA” – 1 roll (3.0 m²) │
│ │
│ [Show details ▼] [Develop Suggested Rolls] │
└──────────────────────────────────────────────────────┘
Behaviour:
On DOMContentLoaded call loadPlanner().
loadPlanner() → GET /api/development/planner/ → render.
“Develop Suggested Rolls” posts the list of roll_ids to /api/development/start/ in one request; back-end starts a session spanning multiple rolls (we already support duration override via film_length so we extend that endpoint to accept multiple rolls).
If advice === “Wait for more rolls”, button is disabled and we show countdown (e.g., “Need at least 1.8 m² more”).
If chemicals are age-locked, button is disabled and a red alert appears.
JS additions:
class DevelopmentDashboard {
…
async loadPlanner() {
try {
const resp = await fetch('/api/development/planner/');
const data = await resp.json();
if (data.success) {
this.renderPlanner(data.run_plan);
}
} catch(err) { console.error(err); }
}
}
Auto refresh every 30 s unless a development session is running.
Database / model touch-ups
No schema change needed for rolls.
Add “multi-roll session” concept: either
a) link each roll to a session_id (already exists) and allow one session to have many rolls; or
b) keep current model but start them sequentially under the hood.
ChemicalBatch model already stores capacity and usage; we only read it.
Algorithm choice notes
The packing problem is basically a 1-D bin‐packing / knapsack with two heuristics (keep projects together, favour many small rolls). A simple greedy with back-tracking to fill 90-95 % works fine in real time (< ms for ~100 rolls).
If you later need global optimality you can switch to dynamic programming or linear programming without changing the API contract.
Extensibility / configurables
Capacity head-room percentage, max chemical age, min utilisation threshold before suggesting a run, project grouping toggle → site settings table.
UI can expose these in an admin panel.
Summary of the requested conditions & how they are satisfied
“Use chemicals in one go” → planner waits until projected_area >= utilisation_threshold (e.g., 80 % of capacity) before recommending a run.
“Ideally under two weeks” → planner checks age of current chemical batches; if they’ll expire before threshold is reached it recommends running sooner, or forces age-locked warning.
“Group by project” → step 3 packs whole project buckets first.
“Optimise by roll count (smaller first)” → within a project or when breaking a large bucket we sort rolls ascending by area.
Independent top section → rendered before roll grid, uses its own API and refresh cycle; roll selection logic stays untouched.
With this design the operator gets a live, data-driven recommendation panel without having to click on any roll first, and the underlying codebase only needs a small self-contained API + a bit of UI work.
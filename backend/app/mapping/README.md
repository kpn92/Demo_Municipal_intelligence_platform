# Mapping backend

This package owns map-specific data assembly.

The first goal is to expose a single operational overview endpoint for the
cleaning MVP. Later this can move to PostGIS-backed tables such as:

- `cleaning_zone`
- `road_segment`
- `map_asset`
- `cleaning_status_event`
- `vehicle_position`
- `route_plan`


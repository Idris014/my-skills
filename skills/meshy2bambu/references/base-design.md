# Printable Character Base Design

## Preserve the character

Keep the imported character mesh, material slots, UVs, and vertex order untouched unless repair was requested. Create the base and mating insert as new objects.

Record a mesh audit before and after the base work. Matching geometry and UV digests demonstrate that the character was not modified.

## Common base patterns

### Compact hidden saddle

Use when the feet must float and the base should be visually hidden.

- Place support under the skirt, hips, hair, or hands.
- Keep the saddle outside foot/shoe projection.
- Validate every leg/shoe component against the base with BVH overlap.

### Wide or round support plate

Use when the skirt and hands need a larger connection region.

- Fit the plate from actual low-contact bounds rather than the whole character bounding box.
- Shift a circular plate rearward when legs must extend beyond the front edge.
- Lower the top surface if it would intersect calves while keeping enough overlap with the hands.
- A visibly round base should use a circular outer contour; do not substitute a rounded rectangle.

### Full-underbody plate

Use only when all low points may touch the base. It conflicts with a suspended-feet requirement unless a leg channel or rearward offset is designed.

## Magnetic interface

A proven small-character interface:

- magnet: `Ø12 × 3 mm`;
- cavity: `Ø12.4 × 3.3 mm`;
- two base holes: `Ø3.0 mm`;
- two insert pins: `Ø2.6 mm`;
- pin spacing: `18 mm`;
- theoretical radial clearance: `0.2 mm`;
- pin roots overlap the insert body by about `0.4 mm` before Boolean union.

Confirm magnet polarity before assembly.

## Geometry quality

- Use at least 96 radial segments for visible circular cavities and 128–192 for a large display disc.
- Bevel exposed edges with a width appropriate to the print scale.
- Avoid coplanar Boolean unions that leave shading seams.
- Prefer a single extruded outline for U shapes or wings.
- Explicitly triangulate Boolean and concave faces before STL export.
- Recalculate face normals.
- Require zero Blender non-manifold edges and one connected component.
- Confirm with Bambu Studio; its STL triangulation can reveal defects hidden by Blender ngons.

## Contact validation

Use BVH triangle overlap instead of relying on renders:

- expected-floating parts: overlap count must be zero;
- required supports: confirm non-zero overlap with the intended skirt, hand, hair, or hip component;
- record foot-to-table or part-to-base clearance in millimetres.

Renders communicate the design, but BVH and importer checks validate it.

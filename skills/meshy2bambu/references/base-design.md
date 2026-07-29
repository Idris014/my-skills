# Printable Base Design and Delivery

Use this reference when adding a display base, plinth, stand, support plate, magnetic interface, or
mounting feature. The base is print engineering, not AI-generated decoration: build it
parametrically after the source geometry has been accepted.

## Base contract

Create `BASE-SPEC.json` from `assets/BASE-SPEC.template.json` before changing geometry. Resolve:

- protected character/product objects;
- objects allowed or required to contact the base;
- objects that must float, especially feet, shoes, hair tips, accessories, and cables;
- outer shape, height, footprint, margin, center offset, top Z, and overlap;
- magnet, pin, insert, screw, or cable features and their tolerances;
- standalone and assembly outputs.

Do not ask about dimensions already supplied by the user or present in a prior accepted version.
If the user asks only for a normal display base, use the safe non-magnetic defaults in the skill.
Pause before inventing a magnet or mating interface because it commits the design to physical
inventory and assembly constraints.

## Preserve the source

Keep imported character/product mesh data, material slots, UVs, vertex order, and transforms
untouched unless repair was requested. Create the base and every precision insert or cutter as new
objects.

Record protected-object geometry signatures before and after base work. Matching vertex, polygon,
material, and UV digests demonstrate that the base operation did not modify the source. Save to a
new Blender master; never overwrite the immutable source or an accepted master.

## Choose the support footprint

Auto-fit from the low-contact/support objects, not automatically from the complete silhouette.
Hair, ears, weapons, tails, or outstretched arms can make whole-object bounds produce an oversized
base.

### Compact hidden saddle

Use when feet must float and the base should be visually hidden.

- Place support under the skirt, hips, back hair, seat, or hands.
- Keep the saddle outside the foot/shoe projection.
- Build this semantically with Blender MCP; it is not a generic plate operation.
- Validate every foot, leg, shoe, and intentionally floating component against the saddle.

### Round display plate

Use for a stable product-like display base or when the user explicitly asks for a circle.

- Fit diameter from the reviewed support footprint plus margin.
- Shift the circle rearward when legs extend beyond the front edge.
- Lower or locally shape the top when it would intersect calves while preserving required hand,
  skirt, hip, or hair contact.
- A visibly round base must use a circular contour; a rounded rectangle is not interchangeable.

### Elliptical plate

Use when the support footprint is clearly wider in one axis and a circle would waste material.
Keep the major/minor axes explicit in the specification.

### Rounded-rectangle plate

Use for product enclosures or display stands whose visual language is rectilinear. Specify corner
radius or bevel and confirm it is not being substituted for a requested circle.

### Full-underbody plate

Use only when every low point may touch the base. It conflicts with suspended feet unless a leg
channel, rearward offset, or raised saddle separates the feet from the plate.

## Parameterized plate builder

Run the bundled script inside Blender:

```bash
blender --background ACCEPTED_MASTER.blend \
  --python scripts/blender_add_print_base.py -- \
  --object Character \
  --support-objects Skirt,LeftHand,RightHand \
  --float-objects LeftFoot,RightFoot \
  --shape circle \
  --height-mm 8 \
  --margin-mm 4 \
  --rearward-offset-mm 3 \
  --contact-overlap-mm 0.3 \
  --output-blend MASTER_WITH_BASE.blend \
  --output-stl Print_Base.stl \
  --output-glb ASSEMBLY_WITH_BASE.glb \
  --report-json BASE-REPORT.json
```

For an already-approved magnetic interface, add:

```text
--magnet-pocket --magnet-diameter-mm 12 --magnet-thickness-mm 3
--magnet-diameter-clearance-mm 0.4 --magnet-depth-clearance-mm 0.3
--locating-holes --pin-hole-diameter-mm 3 --pin-hole-depth-mm 3.5
--pin-spacing-mm 18
```

The script:

- converts millimetres through Blender's scene unit scale;
- creates `Print_Base` as a new mesh and material;
- uses support-object bounds for auto-fit and top placement;
- leaves all protected meshes unchanged;
- optionally cuts a bottom-opening magnet pocket and two top locating holes;
- exports the base alone as STL and the selected assembly as GLB;
- records dimensions, mesh signatures, manifold/component counts, and BVH overlap counts.

Use Blender MCP instead when contact geometry is sculpted, asymmetric, or cannot be expressed by a
plate. The MCP result must still satisfy the same contract and report fields.

## Magnetic interface

A proven starting point for a small character:

- magnet: `Ø12 × 3 mm`;
- cavity: `Ø12.4 × 3.3 mm`;
- two base holes: `Ø3.0 mm`;
- two mating insert pins: `Ø2.6 mm`;
- pin spacing: `18 mm`;
- theoretical magnet radial clearance: `0.2 mm`;
- pin roots overlap an insert body by about `0.4 mm` before Boolean union.

These are not universal defaults. Check the actual magnet, print process, nozzle, shrinkage,
adhesive method, minimum wall/roof, removal access, and mating-side geometry. Record polarity
before assembly. Avoid a fully enclosed magnet cavity unless the manufacturing plan explicitly
captures the magnet during printing.

For a bottom-opening pocket:

- pocket depth is magnet thickness plus depth clearance;
- pocket diameter is magnet diameter plus total diametric clearance;
- leave at least `1.2 mm` roof by default, more for a load-bearing shell;
- add a pry notch only when requested or required for serviceability.

## Geometry quality

- Use at least 96 radial segments for visible circular cavities and 128–192 for a display disc.
- Bevel exposed edges at a width appropriate to print scale.
- Avoid coplanar Boolean unions that leave shading seams.
- Prefer one extruded outline for U-shaped saddles or wings.
- Explicitly triangulate Boolean and concave faces before STL export when the importer needs it.
- Recalculate outward normals.
- Require zero non-manifold edges and one connected component for each standalone solid.
- Confirm with Bambu Studio; STL triangulation can expose problems hidden by Blender ngons.

## Contact and clearance validation

Use BVH triangle overlap rather than relying on renders:

- required support objects: non-zero overlap with the intended base contact region;
- expected-floating objects: zero overlap;
- record the minimum visible foot-to-base clearance in millimetres;
- verify the magnet pocket and holes remain within the base wall/roof envelope.

A zero BVH overlap on an intended support can mean exact tangency rather than a printable union.
Use a small intentional overlap when the parts should print as one body. For a removable
character/base assembly, validate physical seating and clearance instead of forcing an overlap.

Renders communicate the design. Geometry signatures, BVH results, mesh audit, and Bambu import
validate it.

## Required deliverables

When a base is part of the result, include:

- new non-destructive Blender master;
- `BASE-SPEC.json`;
- `BASE-REPORT.json`;
- standalone base STL or 3MF part;
- assembly GLB when appearance review is useful;
- one side or three-quarter contact-clearance render;
- Bambu importer evidence and final package hashes.

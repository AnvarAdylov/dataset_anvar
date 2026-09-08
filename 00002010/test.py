import cadquery as cq
from cadquery.vis import show
from cadquery import selectors


SCALE = 100


sphere_radius = 0.05 * SCALE
hole_radius = 0.015 * SCALE
inner_radius = 0.037 * SCALE
width_wall = 0.013 * SCALE
fillet_radius = 0.004 * SCALE


result = (
    cq.Workplane("XY")
    .sphere(
        radius=sphere_radius - width_wall
    )
    .shell(width_wall)
)

cutter = (
    cq.Workplane("XY", origin=(0, 0, -sphere_radius))
    .cylinder(
        height=sphere_radius,
        radius=hole_radius
    )
)

box = (
    cq.Workplane("XY")
    .box(
        sphere_radius + hole_radius,
        sphere_radius + hole_radius,
        sphere_radius + hole_radius,
        centered=False
    )
    .translate(
        (
            0,
            -sphere_radius - hole_radius,
            0.01 * SCALE
        )
    )
)

# result = result.cut(box)

result = result.cut(
    box.fillet(0.007 * SCALE)
)

selector = selectors.BoxSelector(
    (
        -0.0001 * SCALE,
        -sphere_radius - 0.0001 * SCALE,
        0.0099 * SCALE
    ),
    (
        sphere_radius + 0.0001 * SCALE,
        0.0001 * SCALE,
        sphere_radius + 0.0001 * SCALE
    )
)

opening_edges = result.edges(selector)

result = opening_edges.fillet(fillet_radius)

result = result.cut(cutter)
result = cq.Workplane("XY").newObject([
    result.val().scale(1 / SCALE)
])

show(result)

cq.exporters.export(
    result,
    "00002010/00002010.stl"
)
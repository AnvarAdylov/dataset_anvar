import cadquery as cq
from cadquery.vis import show
from cadquery import selectors

A = 0.022
B = 0.0046
half_height = 0.027
gap_width = 0.008
gap_height = 0.009
full_width = 0.022
inner_radius = 0.0008
depth_cyl = 0.007
space_between = 0.01
hole_offset = 0.005

result = (
    cq.Workplane("XY")
    .rect(
        B, A
    )
    .extrude(half_height)
)
rectangle_cut = (
    cq.Workplane("XY")
    .rect(
        B, gap_width
    )
    .extrude(gap_height)
)
result = result.cut(rectangle_cut)
circleHole1 = (
    cq.Workplane("XY")
    .workplane(offset=half_height-depth_cyl)
    .center(0, hole_offset)
    .circle(inner_radius)
    .extrude(depth_cyl)
)
circleHole2 = (
    cq.Workplane("XY")
    .workplane(offset=half_height-depth_cyl)
    .center(0, -hole_offset)
    .circle(inner_radius)
    .extrude(depth_cyl)
)
result = result.cut(circleHole1)
result = result.cut(circleHole2)
original = result
mirrored = result.mirror("XY")
both = original.union(mirrored)
show(both)
cq.exporters.export(both, "00002019/00002019.stl")


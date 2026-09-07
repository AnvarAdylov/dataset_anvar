import cadquery as cq
from cadquery.vis import show
from cadquery import selectors

A = 0.022
B = 0.0046
gap_width = 0.008
full_width = 0.022
inner_radius = 0.0008
depth_cyl = 0.007
space_between = 0.01

result = (
    cq.Workplane("XY")
    .rect(
        B, A
    )
    .extrude(0.027)
)
rectangle_cut = (
    cq.Workplane("XY")
    .rect(
        B, gap_width
    )
    .extrude(0.009)
)
result = result.cut(rectangle_cut)
circleHole1 = (
    cq.Workplane("XY")
    .workplane(offset=0.02)
    .center(0, 0.005)
    .circle(inner_radius)
    .extrude(0.007)
)
circleHole2 = (
    cq.Workplane("XY")
    .workplane(offset=0.02)
    .center(0, -0.005)
    .circle(inner_radius)
    .extrude(0.007)
)
result = result.cut(circleHole1)
result = result.cut(circleHole2)
original = result
mirrored = result.mirror("XY")
both = original.union(mirrored)
show(both)
cq.exporters.export(both, "00002019/00002019.stl")


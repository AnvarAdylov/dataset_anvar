import cadquery as cq
from cadquery.vis import show
from cadquery import selectors


square_hole = 0.02
top_width = 0.05
top_length = 0.03
height = 0.01
height_square = 0.004
rect_height = 0.006
rect_len = 0.02667
rect_wid = 0.036
side_rect = 0.009
side_rect_len = 0.005
side_rect_wid = 0.0189
cyl_rad = 0.0015
chamfer = 0.001
fillet_rad = 0.0025
fillet_big = 0.005
cyl_height = 0.0045
side_offset = 0.0225


cylinder = (
    cq.Workplane("XZ", origin=(side_offset, 0, cyl_height))
    .cylinder(side_rect_wid, cyl_rad)
    )

result = (
    cq.Workplane("XY")
    .rect(top_width, top_length)
    .extrude(height)

) 
result = (
    result.edges("+Z")
    .fillet(fillet_big)
)
result = (
    result.faces(">Z").edges()
    .fillet(fillet_rad)
)
cutter = (
    cq.Workplane("XY")
    .rect(rect_wid, rect_len)
    .extrude(rect_height)
    )
square_cut = (
    cq.Workplane("XY", origin=(0, 0, rect_height))
    .rect(square_hole, square_hole)
    .extrude(height_square)
    )
side_rect = (
    cq.Workplane("XY", origin=(side_offset, 0, 0))
    .rect(side_rect_len, side_rect_wid )
    .extrude(side_rect)
    )
cutter = cutter.union(square_cut)
cutter = cutter.union(side_rect)
result = result.cut(cutter)
result = result.union(cylinder)
selector = selectors.BoxSelector(
    (
        -square_hole/2-chamfer,
        -square_hole/2-chamfer,
        rect_height+chamfer
    ),
    (
        square_hole/2+chamfer,
        square_hole/2+chamfer,
        height+chamfer
    )
)

opening_edges = result.edges(selector)
result = opening_edges.edges("|X or |Y") .chamfer(chamfer)
show(result)

cq.exporters.export(
    result,
    "00002023/00002023.stl"
)


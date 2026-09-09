import cadquery as cq
from cadquery.vis import show
from cadquery import selectors

width_box = 0.0768# overall length (X)
length_box = 0.0555# overall height (Z)
height_box = 0.0187# overall depth  (Y)
through_square = 0.0018# square through-hole side length
side_wall = 0.002
curve = 0.001 #also space between wall and rectangle hole
rectangle_depth = 0.003#0.002 by 0.0015
roof_thickness = 0.0025 #upper wall with rect
hole_x = 0.0355       # hole center offset from X = 0
hole_y = 0.00645       # hole center offset from Y = 0
notch_x = 0.0254      # notch center offset from X = 0
# box _________________
result = cq.Workplane("front").box(width_box, height_box, length_box, centered=(True, True, False)).faces("+Z").shell(-side_wall)

roof = (
    cq.Workplane("XY")
    .box(
        width_box,
        height_box,
        roof_thickness,
        centered=(True, True, False)
    )
    .translate((0, 0, length_box - roof_thickness))
)

result = result.union(roof)
#_________________ Holes that go throughout
hole_pts = [
    ( hole_x,  hole_y),
    ( hole_x, -hole_y),
    (-hole_x,  hole_y),
    (-hole_x, -hole_y),
]
hole_cutter = cq.Workplane("XY")
for hx, hy in hole_pts:
    hole_cutter = hole_cutter.union(
        cq.Workplane("XY").center(hx, hy).rect(through_square, through_square).extrude(length_box)
    )
result = result.cut(hole_cutter)
# the two notches on roof that will need fillet on inner edges
def make_notch(nx):
    box = (
        cq.Workplane("XY")
        .workplane(offset=length_box - roof_thickness)
        .center(nx, height_box / 2 - rectangle_depth / 2)
        .rect(side_wall, rectangle_depth)
        .extrude(roof_thickness)
    )
    return box

notch_cutter = cq.Workplane("XY")
for nx in (notch_x, -notch_x):
    notch_cutter = notch_cutter.union(make_notch(nx))

result = result.cut(notch_cutter)
# selector box for the inner edge
notch_sel = cq.selectors.BoxSelector(
    (
        -width_box/3,                              # X: left edge of left notch
        height_box/3,      # Y: inset from notch floor
        length_box - roof_thickness,           # Z: inset from notch bottom
    ),
    (
        width_box/3,                               # X: right edge of right notch
        height_box/2,                        # Y: inset from notch opening
        length_box,                            # Z: above the notch top
    ),
)
#
result = (
    result.edges(notch_sel)
    .edges("|X")
    .fillet(curve)
)

show(result)
cq.exporters.export(result, "00002020/00002020.stl")


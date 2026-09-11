from cadquery.vis import show
import cadquery as cq
from cadquery import selectors
import math


od                = 21.0     # tube outer diameter
id_               = 19.0     # tube inner diameter (wall = 1.0 mm)
shaft_d           = 1.5      # central through-shaft diameter

z_shaft_bot       = -0.5     # shaft bottom (below tube)
z_tube_bot        = 4.8      # tube starts
z_cap_start       = 15.0     # tube ends / cap begins
cap_collar_h      = 1.0      # height of the straight collar above z_cap_start, before the taper starts
cap_taper_mid_r   = 5.0      # radius where the taper's mid corner sits
cap_top_z_offset  = 3.0      # height of cap top above z_cap_start (was hardcoded "18")
z_shaft_top       = 21.0     # shaft top (above cap)

cap_collar_top_z  = z_cap_start + cap_collar_h
cap_top_z         = z_cap_start + cap_top_z_offset


arm_half_width    = 2.25     # half-width of the plus arms
cut_extent        = 25.0     # cutter box size; must clear past od/2
cut_z_bot         = z_shaft_bot - 0.5
cut_h             = (z_shaft_top - z_shaft_bot) + 1.0
corner_fillet_r   = 1.5      # radius of the rounded inner corner of each arm
corner_sel_tol    = 1.0      # tolerance used only to *select* the corner-arc edges for chamfering

chamfer_main      = 0.3      # preferred chamfer for the straight + rounded-corner edges
chamfer_safe      = 0.218    # fallback chamfer used only where 0.3 fails (problematic geometry)

hole_r            = 0.75
hole_pos          = 3.5

slot_width        = 1.5
slot_start_r      = 6.0
slot_end_r        = 18.0

cutter_overcut    = 0.2      # extra length cutters extend past the cap top/bottom, to fully punch through
z_cap_top_ref     = cap_top_z + cutter_overcut
export_scale      = 1.0
export_tolerance  = 1e-3
export_ang_tol    = 0.1
out_path          = "00002038/00002038.stl"


tube_h = z_cap_start - z_tube_bot
tube = (
    cq.Workplane("XY")
    .workplane(offset=z_tube_bot)
    .circle(od / 2)
    .circle(id_ / 2)
    .extrude(tube_h)
)

shaft = (
    cq.Workplane("XY")
    .workplane(offset=z_shaft_bot)
    .circle(shaft_d / 2)
    .extrude(z_shaft_top - z_shaft_bot)
)

profile = (
    cq.Workplane("XZ")
    .moveTo(id_ / 2, z_cap_start)           # inner rim top
    .lineTo(id_ / 2, z_tube_bot)            # down inner bore wall
    .lineTo(od / 2, z_tube_bot)             # across bottom of wall
    .lineTo(od / 2, cap_collar_top_z)       # up the od wall
    .lineTo(cap_taper_mid_r, cap_top_z)     # taper down
    .lineTo(shaft_d / 2, cap_top_z)         # across the top face
    .lineTo(shaft_d / 2, z_cap_start)       # down the inner rim
    .close()
)

cap = (
    profile
    .revolve(360, (0, 0, 0), (0, 1, 0))
    .clean()
)


def corner_cutter(sx, sy):
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=cut_z_bot)
        .center(sx * (arm_half_width + cut_extent / 2),
                sy * (arm_half_width + cut_extent / 2))
        .rect(cut_extent, cut_extent)
        .extrude(cut_h)
    )

    inner_corner = (
        cutter.edges("|Z")
        .filter(lambda e:
                (lambda c: c.x * sx > 0 and c.y * sy > 0 and
                           abs(c.x) < arm_half_width + 1 and
                           abs(c.y) < arm_half_width + 1)(e.Center()))
    )
    if inner_corner.size() == 1:
        cutter = inner_corner.fillet(corner_fillet_r)

    return cutter


all_corner_cutters = None
for sx in (1, -1):
    for sy in (1, -1):
        c = corner_cutter(sx, sy)
        all_corner_cutters = c if all_corner_cutters is None else all_corner_cutters.union(c)

cap = cap.cut(all_corner_cutters)


box_sel = cq.selectors.BoxSelector(
    (-12, -12, z_cap_start + 0.5),
    (12, 12, cap_top_z + 0.5),
    boundingbox=False
)


def on_arm_plane(e):
    c = e.Center()
    return abs(abs(c.x) - arm_half_width) < 1e-3 or abs(abs(c.y) - arm_half_width) < 1e-3


def is_corner_arc(e):
    c = e.Center()
    near_corner = any(
        math.hypot(c.x - sx * arm_half_width, c.y - sy * arm_half_width) < corner_sel_tol + 0.5
        for sx in (1, -1) for sy in (1, -1)
    )
    return e.geomType() == "CIRCLE" and near_corner


def is_vertical(e):
    t = e.tangentAt(0)
    return abs(abs(t.z) - 1.0) < 1e-6   # tangent parallel to Z


def edge_fingerprint(e, precision=3):
    c = e.Center()
    return (round(c.x, precision), round(c.y, precision), round(c.z, precision))


def select_edges_by_fingerprint(wp, fingerprints, tol=0.05):
    matched = []
    for e in wp.edges().vals():
        c = e.Center()
        for fx, fy, fz in fingerprints:
            if abs(c.x - fx) < tol and abs(c.y - fy) < tol and abs(c.z - fz) < tol:
                matched.append(e)
                break
    return matched


def chamfer_with_fallback(wp, edge_list, main_val=chamfer_main, safe_val=chamfer_safe):
    if not edge_list:
        return wp

    try:
        return wp.newObject(edge_list).chamfer(main_val)
    except Exception:
        pass

    good_fps = []
    bad_fps = []
    for e in edge_list:
        fp = edge_fingerprint(e)
        try:
            wp.newObject([e]).chamfer(main_val)
            good_fps.append(fp)
        except Exception:
            bad_fps.append(fp)

    result = wp

    if good_fps:
        good_edges = select_edges_by_fingerprint(result, good_fps)
        if good_edges:
            try:
                result = result.newObject(good_edges).chamfer(main_val)
            except Exception:
                bad_fps = good_fps + bad_fps
                good_fps = []

    if bad_fps:
        bad_edges = select_edges_by_fingerprint(result, bad_fps)
        if bad_edges:
            result = result.newObject(bad_edges).chamfer(safe_val)

    return result


arm_edges = (
    cap.edges(box_sel)
    .filter(lambda e: (on_arm_plane(e) or is_corner_arc(e)) and not is_vertical(e))
)

corner_edges = [e for e in arm_edges.vals() if e.geomType() in ("LINE", "CIRCLE")]
cap = chamfer_with_fallback(cap, corner_edges)

new_arm_edges = (
    cap.edges(box_sel)
    .filter(lambda e: (on_arm_plane(e) or is_corner_arc(e)) and not is_vertical(e))
)
taper_edges = [e for e in new_arm_edges.vals() if e.geomType() == "HYPERBOLA"]
cap = chamfer_with_fallback(cap, taper_edges)


cutters = cq.Workplane("XY")
for ang in (0, 90, 180, 270):
    a = math.radians(ang)
    x = hole_pos * math.cos(a)
    y = hole_pos * math.sin(a)

    hole = (
        cq.Workplane("XY")
        .workplane(offset=z_cap_start - cutter_overcut / 2)
        .center(x, y)
        .circle(hole_r)
        .extrude((z_cap_top_ref - z_cap_start))
    )
    cutters = cutters.union(hole)

cap = cap.cut(cutters)
slot_len = slot_end_r - slot_start_r
slot_center_r = (slot_start_r + slot_end_r) / 2

all_cutters = None
for angle in (0, 90, 180, 270):
    slot_cutter = (
        cq.Workplane("XY")
        .workplane(offset=z_cap_start - cutter_overcut / 2)
        .center(slot_center_r, 0)
        .slot2D(slot_len + slot_width, slot_width, 0)
        .extrude(z_cap_top_ref - z_cap_start)
    )
    slot_cutter = slot_cutter.rotate((0, 0, 0), (0, 0, 1), angle)
    all_cutters = slot_cutter if all_cutters is None else all_cutters.union(slot_cutter)

cap = cap.cut(all_cutters)

part = (
    tube
    .union(cap)
    .union(shaft)
    .clean()
)

part = part.newObject([part.val().scale(0.001)])
show(part)
cq.exporters.export(part, "00002038/00002038.stl")


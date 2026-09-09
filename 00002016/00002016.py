import cadquery as cq
from cadquery.vis import show
import math


def build_part(
    outer_r,            # overall outer radius
    height,             # overall height
    rim_wall_r,         # outer radius of the groove (= outer_r - rim wall thickness)
    groove_r,           # inner radius of the groove
    groove_floor_z,     # Z height of the groove floor (measured from bottom)
    flange_inner_r,     # inner radius of the flat top flange (top of center bore)
    bore_r,             # radius of the wide center bore
    bore_chamfer_z,     # Z where the chamfer from flange_inner_r meets bore_r
    shoulder_z,         # Z of the counterbore shoulder floor
    shoulder_inner_r,   # inner radius of the shoulder (start of chamfer to small hole)
    hole_chamfer_z,     # Z where the chamfer meets the small through-hole
    hole_r,             # radius of the small through-hole
    n_beams=12,        # number of support beams in the groove ring
    beam_arc=None, # arc length of each beam; None = equal split (beam == gap)
):
    pts = [
        (hole_r, 0.0),
        (outer_r, 0.0),
        (outer_r, height),
        (rim_wall_r, height),
        (rim_wall_r, groove_floor_z),
        (groove_r, groove_floor_z),
        (groove_r, height),
        (flange_inner_r, height),
        (bore_r, bore_chamfer_z),
        (bore_r, shoulder_z),
        (shoulder_inner_r, shoulder_z),
        (hole_r, hole_chamfer_z),
    ]

    profile = cq.Workplane("XZ").polyline(pts).close()

    solid = profile.revolve(360, (0, 0), (0, 1))
    if n_beams:
        ring_width = rim_wall_r - groove_r


        gap_fraction = 0.945
        pitch_angle = 360.0 / n_beams
        slot_angle = 360.0 / n_beams * gap_fraction   # degrees
        beam_angle = pitch_angle - slot_angle

        slot_profile = (
           cq.Workplane("XZ")
            .polyline([
                (groove_r, -0.001),          
                (rim_wall_r, -0.001),
                (rim_wall_r, height + 0.001),
                (groove_r, height + 0.001),
            ])
            .close()
        )
        one_slot = slot_profile.revolve(slot_angle, (0, 0), (0, 1))

        cutter = cq.Workplane("XY")
        for i in range(n_beams):
            ang = beam_angle / 2.0 + pitch_angle * i
            cutter = cutter.union(
                one_slot.rotate((0, 0, 0), (0, 0, 1), ang)
            )

        solid = solid.cut(cutter)
    show(solid)
    return solid


part_small = build_part(
    outer_r=0.03580,
    height=0.00600,
    rim_wall_r=0.03500,
    groove_r=0.03200,
    groove_floor_z=0.00050,
    flange_inner_r=0.01900,
    bore_r=0.01800,
    bore_chamfer_z=0.00500,
    shoulder_z=0.00260,
    shoulder_inner_r=0.00455,
    hole_chamfer_z=0.00160,
    hole_r=0.00355,
    n_beams=12,
)


if __name__ == "__main__":
    cq.exporters.export(part_small, "00002016/00002016.stl", tolerance=1e-6, angularTolerance=0.05)


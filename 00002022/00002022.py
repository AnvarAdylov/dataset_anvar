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
    beam_arc=None, # arc length of each beam;
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
        mid_r = (rim_wall_r + groove_r) / 2.0

        if beam_arc is None:
            beam_arc = (2.0 * math.pi * mid_r / n_beams) / 2.0
        ring_profile = (
            cq.Workplane("XZ")
            .polyline([
                (groove_r, -0.001),
                (rim_wall_r, -0.001),
                (rim_wall_r, height + 0.001),
                (groove_r, height + 0.001),
            ])
            .close()
        )
        ring_solid = ring_profile.revolve(360, (0, 0), (0, 1))
        solid = solid.cut(ring_solid)
        beam_box = (
            cq.Workplane("XY")
             .box(ring_width, beam_arc, groove_floor_z + beam_arc,
                 centered=(True, True, False))
            .translate((mid_r, 0, groove_floor_z-0.001))
        )

        trim_profile = (
            cq.Workplane("XZ")
            .polyline([
                (groove_r, 0),
                (rim_wall_r, 0),
                (rim_wall_r, groove_floor_z),
                (groove_r, groove_floor_z),
            ])
            .close()
        )
        trim_solid = trim_profile.revolve(360, (0, 0), (0, 1))

        beam = beam_box.intersect(trim_solid)

        for i in range(n_beams):
            solid = solid.union(
                beam.rotate((0, 0, 0), (0, 0, 1), 360.0 / n_beams * i)
            )
    show(solid)
    return solid


part_large = build_part(
    outer_r=0.04080,
    height=0.00400,
    rim_wall_r=0.04000,
    groove_r=0.03650,
    groove_floor_z=0.00050,
    flange_inner_r=0.02050,
    bore_r=0.01950,
    bore_chamfer_z=0.00300,
    shoulder_z=0.00260,
    shoulder_inner_r=0.00323,
    hole_chamfer_z=0.00210,
    hole_r=0.00273,
    n_beams=12,
    beam_arc=0.001
)

if __name__ == "__main__":
    cq.exporters.export(part_large, "00002022/00002022.stl", tolerance=1e-6, angularTolerance=0.05)
    


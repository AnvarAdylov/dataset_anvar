import cadquery as cq
from cadquery.vis import show

cyl_height = 0.1524
cyl_radius = 0.00635
rivet = 0.000788

result = (
    cq.Workplane("XY")
    .cylinder(
        height=cyl_height,
        radius=cyl_radius
    )
    .chamfer(rivet)
)


print("Model created successfully")
show(result)
cq.exporters.export(result, "00002002/00002002.stl")


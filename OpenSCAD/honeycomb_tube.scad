use <cylinder_outer.scad>

module honeycomb_model(d=50, h=100, num=12, spacing=1.5, edges=6)
{
    gapRot = (spacing / d) * 180 / PI;
    hexRot = (360 - gapRot * num) / num;
    totalRot = hexRot + gapRot;
    hexDiam = d * sin(hexRot / 2);
    hexLen = d *.52;
    z_step = sin(60) * hexDiam + sin(60) * spacing;
    for(y = [0 : h / z_step]) {
        translate([0,0, y * z_step]) 
        for(x = [0 : (num - 1)]) {
            rotate([0,0, x * totalRot + totalRot / 2 * (y % 2)]) 
            translate([0,hexLen/2,0])
            rotate([90,90,0])
            cylinder(h=hexLen, d=hexDiam, $fn=edges, center=true);
        }
    }
}

module honeycomb_tube(od=50, id=48, h=100, num=12, spacing=1.5, edges=6, capThickness=2) {
    difference() {
        cylinder_outer(h=h, d=od);
        cylinder_outer(h=h, d=id);
        honeycomb_model(d=od, h=h, num=num, spacing=spacing, edges=edges);
    }

    // Cylinder end caps
    difference() {
        cylinder_outer(h=h, d=od);
        cylinder_outer(h=h, d=id);
        cutboxH = h - capThickness*2;
        translate([0, 0, cutboxH/2 + capThickness]) cube([od + 1, od + 1, cutboxH], center=true);
    }
}

honeycomb_model();
honeycomb_tube();
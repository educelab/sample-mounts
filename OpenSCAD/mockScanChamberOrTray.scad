chamber_diameter = 61.16;
chamber_length = 150;
wall_thickness = 2.5;
end_wall_width_from_outer_diameter = 4;
open_tray=true;

difference() {
    union() {
        difference() {
            cylinder(
            h=chamber_length + wall_thickness,
            d=chamber_diameter + wall_thickness*2, 
            center=true, 
            $fa=1, 
            $fs=0.5);
            cylinder(
            h=chamber_length + wall_thickness + 1, 
            d=chamber_diameter, 
            center=true, 
            $fa=1, 
            $fs=0.5);
        }

        translate([0,0,-(chamber_length / 2)]) {
            difference() {
                cylinder(
                h=wall_thickness, 
                d=chamber_diameter + wall_thickness*2, 
                center=true,
                $fa=1, 
                $fs=0.5);
                cylinder(
                h=wall_thickness + 1,
                d=chamber_diameter - end_wall_width_from_outer_diameter,
                center=true,
                $fa=1, 
                $fs=0.5);
            }
        }
    }
    if (open_tray) {
        translate([-5000,0,-5000])
        cube([10000,10000,10000]);
    }
}
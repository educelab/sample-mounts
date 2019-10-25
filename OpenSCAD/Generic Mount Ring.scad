depth = 1.76;
rad_lg = 22.45;
rad_sm = 13.5/2 - 1;

module GenericMountRing() {
    translate([0,0,-1.5]) difference() {
        import("../Models/Generic Mount Ring.stl");
        translate([0,0,-1.1]) scale([1,1, depth/rad_lg]) sphere(rad_lg, $fn=64);
        translate([0,0,.725]) scale([1,1, 1/rad_sm]) sphere(rad_sm, $fn=64);
    }
}

GenericMountRing();

         
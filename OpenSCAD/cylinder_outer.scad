 module cylinder_outer(h, d=1, r, center=false, fn=48){
   rad = !is_undef(r) ? r : d/2;
   fudge = 1/cos(180/fn);
   cylinder(h=h,r=rad*fudge,center=center,$fn=fn);
}
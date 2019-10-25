function polyMax(p) = [max([for(pi = p) pi[0]]), max([for(pi = p) pi[1]])];
function polyMin(p) = [min([for(pi = p) pi[0]]), min([for(pi = p) pi[1]])];
function polyMidPt(p) = (polyMin(p) + polyMax(p))/2;

// spirals     = how many spirals (positive=CCW, negative=CW)
// thickness   = how thick you want the arms to be
// startradius = beginning radius position
// spacing     = spacing between radial points
// startangle  = angle to begin first sweep
// armCenter   = 'true' armCenters the spiral arm thickness
// center      = 'true' center spiral on origin
// original from: https://www.thingiverse.com/thing:2945256
module archimedean_spiral_2d(spirals=1, thickness=1, spacing=1, startradius=1.0, startangle=0, armCenter=true, center=false) {
	t = thickness;
	s1 = (startradius / spacing) * 360.0;
	s2 = ((startradius + (abs(spirals)*spacing)) / spacing) * 360.0;
	angoff = ((-s1+startangle) % 360.0);
	a = sqrt(pow(spacing*abs(spirals)+startradius,2)/(pow(s2,2)*(pow(cos(s2),2) + pow(sin(s2),2))));
	points=[
		for(i = [s1+($fa - (s1 % $fa))-$fa:$fa:s2+($fa - (s2 % $fa))-$fa]) [
			(((i*a)+ ((armCenter) ? -t/2 : 0))*cos(sign(spirals)*(i+angoff))),
			(((i*a)+ ((armCenter) ? -t/2 : 0))*sin(sign(spirals)*(i+angoff)))
		]
	];
	points_inner=[
		for(i = [s2+($fa - (s2 % $fa))-$fa:-$fa:s1+($fa - (s1 % $fa))-$fa]) [
			(((i*a)+ ((armCenter) ? t/2 : t))*cos(sign(spirals)*(i+angoff))),
			(((i*a)+ ((armCenter) ? t/2 : t))*sin(sign(spirals)*(i+angoff)))
		]
	];
    
    translation = center ? -polyMidPt(concat(points,points_inner)) : [0,0];
	translate(translation) polygon(concat(points,points_inner));
}

module archimedean_spiral_3d(height = 5, spirals=1, thickness=1, spacing = 1, startradius = 1.0, startangle = 0, armCenter=true, center=false)
{
    linear_extrude(height=height){ 
        archimedean_spiral_2d(spirals=spirals, thickness=thickness, spacing=spacing, startradius=startradius, startangle=startangle, armCenter=armCenter, center=center); 
    }
}

// archimedean_spiral_3d(thickness=5, spirals=5, startradius=5, spacing=10, center=true);
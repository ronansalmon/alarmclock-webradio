
$fn = 60;
h = 10;
r_out = 5;
r_in = 1;

difference(){
  cylinder(h, r_out, r_out, center=true,$fn = 6);
  cylinder(h*2, r_in, r_in, center = true);
}
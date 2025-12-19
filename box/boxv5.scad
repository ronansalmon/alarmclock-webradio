
wallthickness = 1; // this is the wall of the lip, the box is twice as thick
internalx = 100; // internal x dimension
internaly = 80; // internal y dimension
internalz = 60; // internal overall z dimension
internal_lidz=90; // this is taken of off the internalz for the bottom height and acts as the lid internal height
led_x = 62.4;
led_y = 40.2;
cable_hole = 6;
rotary_hole = 6.9/2;

lip_overlap = 3.5; // how much overlap between box and lid, this works as a default but can be shrunk as needed

//#############################
// INTERNAL VARIABLES, DO NOT MODIFY
internal_botz=internalz-lip_overlap*2;

actual_y=internaly+(4*wallthickness);
actual_x=internalx+(4*wallthickness);
actual_lidz=internal_lidz+(2*wallthickness);
actual_botz=internal_botz+(2*wallthickness);

lip_x = internalx+(2*wallthickness);
lip_y = internaly+(2*wallthickness);

echo(actual_y);
echo(actual_x);
echo(actual_lidz);
echo(internal_lidz);
echo(lip_x);
echo(lip_y);

//###########################
module led() {
  cube([led_x, led_y, lip_overlap+.3]);
}

module rotary() {
  cylinder(r = rotary_hole, h = actual_lidz+lip_overlap, $fn = 30);
}

module bottom() {
  difference() {
    union() {
      cube([actual_x,actual_y,actual_botz]);
      translate([wallthickness,wallthickness,actual_botz])
        cube([lip_x,lip_y,lip_overlap]);
        
    }
    translate([(2*wallthickness),(2*wallthickness),(2*wallthickness)])
      cube([internalx,internaly,internalz]);

    // lock
    translate([wallthickness, internaly/4, actual_botz+lip_overlap/2])
      rotate([-90,0,0])
        cylinder(r = 0.5, h = internaly/2, $fn = 30);
    translate([lip_x+wallthickness, internaly/4, actual_botz+lip_overlap/2])
      rotate([-90,0,0])
        cylinder(r = 0.5, h = internaly/2, $fn = 30);


    translate([(2*wallthickness+internalx/2-led_x/2),(2*wallthickness+internaly/2-led_y/2),-0.1])
      rotate([0,0,0])
        led();

        
    translate([lip_x/5*1.5,5,35])
      rotate([90,0,0])
        rotary();
    translate([lip_x/5*3.5,5,35])
      rotate([90,0,0])
        rotary();
  }
}


module lid() {
  union() {
    difference() {
      cube([actual_x,actual_y,actual_lidz]);
      
      translate([(2*wallthickness),(2*wallthickness),-.1])
        cube([internalx,internaly,internal_lidz-.1]);
      
      translate([(wallthickness),(wallthickness),-.1])
        cube([lip_x,lip_y,lip_overlap+.3]);
      
      // passe cable
      translate([internalx/2,lip_y,-.1])
        cylinder(r = 7.5, h = actual_lidz+1, $fn = 30);
    }
    
    // lock
    translate([wallthickness, internaly/2-(internaly/2.2/2), lip_overlap/2])
      rotate([-90,0,0])
        cylinder(r = 0.4, h = internaly/2.2, $fn = 30);
    translate([internalx+wallthickness*3, internaly/2-(internaly/2.2/2), lip_overlap/2])
      rotate([-90,0,0])
        cylinder(r = 0.4, h = internaly/2.2, $fn = 30);
  }
}


*bottom();
translate([0,-10,actual_lidz])
  rotate([180,0,0])
    lid();





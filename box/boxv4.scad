
wallthickness = 1; // this is the wall of the lip, the box is twice as thick
internalx = 100; // internal x dimension
internaly = 80; // internal y dimension
internalz = 60; // internal overall z dimension
internal_lidz=45; // this is taken of off the internalz for the bottom height and acts as the lid internal height
led_x = 62.4;
led_y = 40.2;
cable_hole = 6;
rotary_hole = 6.9/2;

lip_overlap = 2.5; // how much overlap between box and lid, this works as a default but can be shrunk as needed

lipspacing=0; // this amount is take off of the wall thickness on the lip to increase spacing, if your lid is too tight you can increase this but it will reduce the actual wall thickness on the lip so too much and you will have to increase the wallthickness to compensate. Should be 0 in ideal world, you will likely be better just lightly sanding the lip unless your printer is way out

//#############################
// INTERNAL VARIABLES, DO NOT MODIFY
internal_botz=internalz-lip_overlap*2;

actual_y=internaly+(4*wallthickness);
actual_x=internalx+(4*wallthickness);
actual_lidz=lip_overlap*2+(2*wallthickness);
actual_botz=internal_botz+(2*wallthickness);

lip_x = internalx+(2*wallthickness);
lip_y = internaly+(2*wallthickness);


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
  difference() {
    cube([actual_x,actual_y,actual_lidz+internal_lidz]);
    
    translate([(2*wallthickness),(2*wallthickness),-.1])
      cube([internalx,internaly,internal_lidz+lip_overlap+.1]);
    
    translate([(wallthickness)-lipspacing/2,(wallthickness)-lipspacing/2,-.1])
      cube([lip_x+lipspacing,lip_y+lipspacing,lip_overlap+.3]);
    
    // passe cable
    #translate([internalx,lip_y-7.5,wallthickness])
      rotate([0,90,0])
        cylinder(r = 7.5, h = 10, $fn = 30);
  }
}

*translate([0,0,actual_botz + internal_lidz + 10])lid();
bottom();
*translate([0,0,(internal_lidz + 10)-3])
  rotate([180,0,0])
    lid();





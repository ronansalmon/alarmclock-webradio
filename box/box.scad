include <connecteurs.scad>

xb=120;
yb=120;
zb=70;
oledx=62.7;
oledy=39;
rotary=3;
ep=3;
creneau=ep*3;

//monte();
projectionZ() decoupe();
//coteD();


module monte() {
  fond();
  coteG();
  translate([xb-ep,0,0]) coteD();
  arriere();
}

module decoupe() {
  dessus();
  translate([0,zb+yb+20,0]) fond();
  translate([0,-10,0]) rotate([90,0,0]) avant();
  translate([0,zb+yb+10,0]) rotate([90,0,0]) arriere();
  translate([-20,0,0]) rotate([0,-90,0]) coteG();
  translate([xb+20,0,0]) rotate([0,90,0]) coteD(); 
}

module fond() {
  union() {
    translate([ep,ep,0]) cube([xb-2*ep,yb-ep,ep]);
    translate([ep,0,0]) connecteurMale([xb-2*ep,ep,ep],[creneau,0,0],[.1,0,0]);
    translate([ep,yb,0]) connecteurMale([xb-2*ep,ep,ep],[creneau,0,0],[.1,0,0]);
    translate([0,ep,0]) connecteurMale([ep,yb-ep,ep],[0,creneau,0],[0,0.1,0]);
    translate([xb-ep,ep,0]) connecteurMale([ep,yb-ep,ep],[0,creneau,0],[0,0.1,0]);
  }
}

module dessus() {
  difference() {
    fond();
    // rotary encoder
    translate([xb/2.75,yb/4,-1]) cylinder(ep*2, rotary, rotary, $fn=30);
    translate([xb/1.50,yb/4,-1]) cylinder(ep*2, rotary, rotary, $fn=30);
  }
}
module coteG() {
  difference() {
    union() {
      translate([0,ep,0]) cube([ep,yb-ep,zb]);
      connecteurMale([ep,ep,zb],[0,0,creneau],[0,0,0.1]);
      translate([0,yb,0]) connecteurMale([ep,ep,zb],[0,0,creneau],[0,0,0.1]);
    }
    translate([0,ep,0]) connecteurFemelle([ep,yb-ep,ep],[0,creneau,0],[0,0.1,0]);
    translate([0,ep,zb-ep]) connecteurFemelle([ep,yb-ep,ep],[0,creneau,0],[0,0.1,0]);
  }
}
module coteD() {
  cote = 10;
  difference() {
    coteG();
    translate([-5,yb-ep*2-cote-60,zb-cote-ep]) cube([cote,cote+10,cote]);
  }
}
module arriere() {
  difference() {
    cube([xb,ep,zb]);
    connecteurFemelle([ep,ep,zb],[0,0,creneau],[0,0,0.2]);
    translate([xb-ep,0,0]) connecteurFemelle([ep,ep,zb],[0,0,creneau],[0,0,0.1]);
    translate([ep,0,0]) connecteurFemelle([xb-2*ep,ep,ep],[creneau,0,0],[.1,0,0]);
    translate([ep,0,zb-ep]) connecteurFemelle([xb-2*ep,ep,ep],[creneau,0,0],[.1,0,0]);
  }
}


module avant() {
  difference() {
    arriere();
    // oled
    translate([xb/2-oledx/2,-1,zb/2-oledy/2]) cube([oledx,ep*2, oledy]);
  }
}
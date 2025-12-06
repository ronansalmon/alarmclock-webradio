/* module connecteurs 
  CCr- 2023
  
  usage : 
  connecteurMale(dim=[],teton=[],jeux=[])
  exemple pour une piece de 40x10 en 5 d'epaisseur
  cube([40,10,5]);
  connecteurMale([40,5,5],[8,0,0],[.2,0,0]);
  */
  
  
module connecteurMale(dimensions,teton,jeu)
{
    nb=teton.x!=0?floor(dimensions.x/(2*teton.x)):teton.y!=0?floor(dimensions.y/(2*teton.y)):floor(dimensions.z/(2*teton.z));

    l1=teton.x!=0?(dimensions.x-nb*2*teton.x)/2:teton.y!=0?(dimensions.y-nb*2*teton.y)/2:(dimensions.z-nb*2*teton.z)/2;
    
    for(i=[0:1:nb-1]) 
    {
       xp=(teton.x!=0?l1+2*teton.x*i+teton.x/2:0)+jeu.x/4;
       yp=(teton.y!=0?l1+2*teton.y*i+teton.y/2:0)+jeu.y/4;
       zp=(teton.z!=0?l1+2*teton.z*i+teton.z/2:0)+jeu.z/4;
                
       xt=(teton.x!=0?teton.x:dimensions.x)-jeu.x/2;
       yt=(teton.y!=0?teton.y:dimensions.y)-jeu.y/2;
       zt=(teton.z!=0?teton.z:dimensions.z)-jeu.z/2;
       
       translate([xp,yp,zp]) cube([xt,yt,zt]);
    } 
}

module connecteurFemelle(dimensions,teton,jeu)
{
    nb=teton.x!=0?floor(dimensions.x/(2*teton.x)):teton.y!=0?floor(dimensions.y/(2*teton.y)):floor(dimensions.z/(2*teton.z));

    l1=teton.x!=0?(dimensions.x-nb*2*teton.x)/2:teton.y!=0?(dimensions.y-nb*2*teton.y)/2:(dimensions.z-nb*2*teton.z)/2;
    
    for(i=[0:1:nb-1]) 
    {
       xp=(teton.x!=0?l1+2*teton.x*i+teton.x/2:0)-jeu.x/4;
       yp=(teton.y!=0?l1+2*teton.y*i+teton.y/2:0)-jeu.y/4;
       zp=(teton.z!=0?l1+2*teton.z*i+teton.z/2:0)-jeu.z/4;
                
       xt=(teton.x!=0?teton.x:dimensions.x)+jeu.x/2;
       yt=(teton.y!=0?teton.y:dimensions.y)+jeu.y/2;
       zt=(teton.z!=0?teton.z:dimensions.z)+jeu.z/2;
       
       translate([xp,yp,zp]) cube([xt,yt,zt]);
    } 
}

module projectionY()
{
    projection(cut = false) rotate([90,0,0]) children();
}

module projectionX()
{
    projection(cut = false) rotate([0,90,0]) children();
}

module projectionZ()
{
    projection(cut = false) children();
}

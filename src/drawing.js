/* Original drawing primitives; deterministic at arbitrary musical time. */
const W=1920,H=1080,TAU=Math.PI*2;
const C={ink:'#263b4a',paper:'#fff5dd',coral:'#ef785f',yellow:'#f7ca65',teal:'#459b9b',mint:'#a8cbb6',blue:'#6b95bc',plum:'#695a83',flame:'#ff4b35',cyan:'#55e6ff'};
let ctx;
const clamp=(a,l=0,h=1)=>Math.min(h,Math.max(l,a)),mix=(a,b,u)=>a+(b-a)*u;
const ease=u=>{u=clamp(u);return u*u*(3-2*u)},seed=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const pulse=t=>{const p=(t-MUSIC.phase)/MUSIC.beat_period;return Math.exp(-Math.max(0,p-Math.floor(p))*6)};
function path(points,fill,stroke=C.ink,lw=3,close=true){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));if(close)ctx.closePath();ctx.fillStyle=fill;if(fill)ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=lw;ctx.stroke()}}
function ellipse(x,y,rx,ry,fill,stroke=null,lw=3){ctx.beginPath();ctx.ellipse(x,y,Math.abs(rx),Math.abs(ry),0,0,TAU);ctx.fillStyle=fill;if(fill)ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=lw;ctx.stroke()}}
function line(points,color=C.ink,w=3){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=w;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke()}
function curve(points,color=C.ink,w=3){ctx.beginPath();ctx.moveTo(...points[0]);for(let i=1;i<points.length;i+=3)ctx.bezierCurveTo(...points[i],...points[i+1],...points[i+2]);ctx.strokeStyle=color;ctx.lineWidth=w;ctx.lineCap='round';ctx.stroke()}
function roundRect(x,y,w,h,r,fill,stroke=null,lw=3){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=lw;ctx.stroke()}}
function star(x,y,r,color,rot=0,n=5){let p=[];for(let i=0;i<n*2;i++){let a=rot+i*Math.PI/n-Math.PI/2,rr=i%2?r*.44:r;p.push([x+Math.cos(a)*rr,y+Math.sin(a)*rr])}path(p,color,null)}
function heart(x,y,r,color){ctx.save();ctx.translate(x,y);ctx.scale(r/30,r/30);ctx.beginPath();ctx.moveTo(0,24);ctx.bezierCurveTo(-55,-7,-17,-43,0,-16);ctx.bezierCurveTo(17,-43,55,-7,0,24);ctx.fillStyle=color;ctx.fill();ctx.restore()}
function text(str,x,y,size,color=C.ink,font='HandBold',align='center'){ctx.font=`${size}px ${font}`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillStyle=color;ctx.fillText(str,x,y)}
function paperPlane(x,y,s=1,a=0){ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.scale(s,s);path([[-65,-25],[72,0],[-32,47],[-17,9]],'#fff9e9',C.ink,3);path([[-65,-25],[-17,9],[72,0]],'#f4c965',C.ink,2);line([[-17,9],[-32,47],[3,13]],C.ink,2);ctx.restore()}
function cloud(x,y,s,c='#fff8e5'){ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.beginPath();ctx.moveTo(-120,35);ctx.bezierCurveTo(-166,7,-119,-34,-84,-23);ctx.bezierCurveTo(-89,-80,-12,-103,19,-54);ctx.bezierCurveTo(61,-90,117,-52,107,-13);ctx.bezierCurveTo(170,-21,182,42,130,47);ctx.closePath();ctx.fillStyle=c;ctx.fill();ctx.globalAlpha*=.25;curve([[-110,35],[-40,48],[59,36],[125,40]],C.blue,2);ctx.restore()}
function sparkle(x,y,r,c){line([[x-r,y],[x+r,y]],c,2.5);line([[x,y-r],[x,y+r]],c,2.5);ellipse(x,y,2,2,c)}
function blossom(x,y,r,c){for(let i=0;i<5;i++){let a=i*TAU/5;ellipse(x+Math.cos(a)*r*.7,y+Math.sin(a)*r*.7,r*.55,r*.55,c)}ellipse(x,y,r*.35,r*.35,C.yellow)}
function leaf(x,y,s,a,color){ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.beginPath();ctx.moveTo(0,0);ctx.quadraticCurveTo(-s*.8,-s*.7,0,-s*1.8);ctx.quadraticCurveTo(s*.85,-s*.7,0,0);ctx.fillStyle=color;ctx.fill();line([[0,0],[0,-s*1.5]],'#e4e5b5',1.4);ctx.restore()}
function scribbleCircle(x,y,r,c){for(let k=0;k<2;k++){ctx.beginPath();for(let i=0;i<=60;i++){let a=i*TAU/60;let rr=r+Math.sin(a*7+k)*2;let p=[x+Math.cos(a)*rr,y+Math.sin(a)*rr*.7];i?ctx.lineTo(...p):ctx.moveTo(...p)}ctx.strokeStyle=c;ctx.lineWidth=2;ctx.stroke()}}
function impactBurst(x,y,r,t,color=C.flame){let p=pulse(t),rr=r*(.78+p*.48);ctx.save();ctx.translate(x,y);ctx.globalAlpha=.52+p*.42;for(let i=0;i<18;i++){let a=i*TAU/18,inner=rr*(.39+(i%2)*.1),outer=rr*(.91+(i%3)*.15);line([[Math.cos(a)*inner,Math.sin(a)*inner],[Math.cos(a)*outer,Math.sin(a)*outer]],i%2?color:C.cyan,7+(i%3)*2)}ctx.globalAlpha=.72+p*.25;scribbleCircle(0,0,rr*.49,color);ctx.globalAlpha=.6+p*.3;scribbleCircle(0,0,rr*.58,C.cyan);ctx.restore()}
function speedLines(t,energy=1){ctx.save();ctx.globalAlpha=.20+energy*.21;for(let i=0;i<25;i++){let y=(i*67+t*(460+seed(i)*320))%(H+180)-90,x=seed(i+91)*W,len=120+seed(i+39)*500;line([[x,y],[x-len,y+48]],i%2?'#55e6ff':'#ff6844',2+seed(i)*2.6)}ctx.restore()}

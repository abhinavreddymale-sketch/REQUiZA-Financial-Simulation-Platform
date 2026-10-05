const assert=require('assert'),E=require('../engine/engine.js');
const near=(a,b,t,m)=>assert(Math.abs(a-b)<=t,m+': got '+a+' expected '+b);
let r=E.sip(2000,10,12);near(r.fv,464678,1,'T1');assert.strictEqual(r.inv,240000);
assert.strictEqual(E.sip(2000,10,0).fv,240000);
r=E.emi(50000,12,12);near(r.emi,4442.44,.01,'T3 emi');near(r.tot,53309.28,.1,'T3 total');
assert.strictEqual(E.emi(12000,0,12).emi,1000);
near(E.infl(1e5,6,10),55839,1,'T5');
near(E.ann(5),79.59,.01,'T6a');near(E.ann(30),2229.8,.1,'T6b');
near(E.bond(1000,.08,5,.1),924.18,.01,'T7 price');near(E.ytm(1000,.08,5,924.18),.1,1e-4,'T7 ytm');
near(E.vol2(.5,.5,.2,.1,.2)*100,12.04,.01,'T8');
const A=E.mc(1000,5,.1,.2,200,7),B=E.mc(1000,5,.1,.2,200,7);assert.deepStrictEqual(A,B);
const t=A.map(x=>x[60]);assert(E.pct(t,.05)<E.pct(t,.5)&&E.pct(t,.5)<E.pct(t,.95));
const R=E.rng(11),T=[];for(let i=0;i<20000;i++){const z=Math.sqrt(-2*Math.log(Math.max(R(),1e-12)))*Math.cos(2*Math.PI*R());T.push(Math.exp(.8+.2*Math.sqrt(10)*z))}
assert(Math.abs(E.pct(T,.5)/Math.exp(.8)-1)<.02,'T9 median');
const am=E.amort(50000,12,12);assert(Math.abs(am.bal)<1&&Math.abs(am.sp-50000)<1,'T10');
for(const f of [E.sip(100,1,0).fv,E.emi(1000,0,1).emi])assert(Number.isFinite(f));
console.log('All engine tests passed (T1-T10 + finite checks)');

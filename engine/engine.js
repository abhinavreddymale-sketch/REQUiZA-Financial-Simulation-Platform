// Framework-free engine, extracted from the site so tests and the site share one source.
const E={
sip(P,y,a){const r=a/1200,n=y*12;return{inv:P*n,fv:r===0?P*n:P*((Math.pow(1+r,n)-1)/r)*(1+r)}},
emi(P,a,n){const r=a/1200,e=r===0?P/n:P*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);return{emi:e,tot:e*n,int:e*n-P}},
amort(P,a,n){const r=a/1200,e=E.emi(P,a,n).emi;let b=P,sp=0;for(let i=0;i<n;i++){const it=b*r,pr=e-it;sp+=pr;b-=pr}return{bal:b,sp}},
infl:(v,i,t)=>v/Math.pow(1+i/100,t),ann:m=>(Math.pow(1+m/100,12)-1)*100,
bond(F,c,N,y){let p=0;for(let t=1;t<=N;t++)p+=F*c/Math.pow(1+y,t);return p+F/Math.pow(1+y,N)},
ytm(F,c,N,P){let lo=0,hi=1;for(let i=0;i<100;i++){const m=(lo+hi)/2;E.bond(F,c,N,m)>P?lo=m:hi=m}return(lo+hi)/2},
vol2:(w1,w2,s1,s2,r)=>Math.sqrt(w1*w1*s1*s1+w2*w2*s2*s2+2*w1*w2*r*s1*s2),
rng(s){return()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}},
mc(P,yrs,mu,sg,paths,seed){const R=E.rng(seed),dt=1/12,n=yrs*12,out=[],dr=(mu-sg*sg/2)*dt,vs=sg*Math.sqrt(dt);
for(let p=0;p<paths;p++){let s=0;const a=[0];for(let m=1;m<=n;m++){const z=Math.sqrt(-2*Math.log(Math.max(R(),1e-12)))*Math.cos(2*Math.PI*R());s=(s+P)*Math.exp(dr+vs*z);a.push(s)}out.push(a)}return out},
pct(a,q){const s=[...a].sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.floor(q*s.length))]}};

module.exports=E;

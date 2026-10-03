// Exact / large-sample EV engine for story stages. Card = rank*4+suit, suits s,h,d,c = 0..3.
const RANKS='23456789TJQKA',SUITS='shdc';
const card=s=>RANKS.indexOf(s[0])*4+SUITS.indexOf(s[1]);
const cards=s=>s.trim().split(/\s+/).map(card);
const cr=c=>c>>2,cs=c=>c&3;
function strHi(b){for(let h=12;h>=4;h--){const m=0x1f<<(h-4);if((b&m)===m)return h}if((b&0x100f)===0x100f)return 3;return -1}
function ev(c){const rc=new Array(13).fill(0),sc=[0,0,0,0],sb=[0,0,0,0];let rb=0;
  for(const x of c){const r=x>>2,s=x&3;rc[r]++;sc[s]++;sb[s]|=1<<r;rb|=1<<r}
  for(let s=0;s<4;s++)if(sc[s]>=5){const h=strHi(sb[s]);if(h>=0)return 8<<20|h<<16;const k=[];for(let r=12;r>=0&&k.length<5;r--)if(sb[s]>>r&1)k.push(r);return 5<<20|k[0]<<16|k[1]<<12|k[2]<<8|k[3]<<4|k[4]}
  let q=-1;const t=[],p=[],s1=[];for(let r=12;r>=0;r--){if(rc[r]===4)q=r;else if(rc[r]===3)t.push(r);else if(rc[r]===2)p.push(r);else if(rc[r]===1)s1.push(r)}
  if(q>=0){let k=0;for(let r=12;r>=0;r--)if(r!==q&&rc[r]){k=r;break}return 7<<20|q<<16|k<<12}
  if(t.length&&(t.length>1||p.length)){const pp=t.length>1?Math.max(t[1],p[0]??-1):p[0];return 6<<20|t[0]<<16|pp<<12}
  const h=strHi(rb);if(h>=0)return 4<<20|h<<16;
  if(t.length){const ks=[...p,...s1].sort((a,b)=>b-a);return 3<<20|t[0]<<16|(ks[0]??0)<<12|(ks[1]??0)<<8}
  if(p.length>=2){const ks=[...p.slice(2),...s1].sort((a,b)=>b-a);return 2<<20|p[0]<<16|p[1]<<12|(ks[0]??0)<<8}
  if(p.length){return 1<<20|p[0]<<16|(s1[0]??0)<<12|(s1[1]??0)<<8|(s1[2]??0)<<4}
  return s1[0]<<16|s1[1]<<12|s1[2]<<8|s1[3]<<4|s1[4]}
// best 5 of up to 7 (ev handles 5..7 directly via counting — fine for 7-card max)
const score=(h,b)=>ev([...h,...b]);
// ---- ranges: "AKs AKo AK 99 Qs9h A9s:0.5" ----
function combosOfToken(tok){const out=[];
  if(/^[2-9TJQKA][shdc][2-9TJQKA][shdc]$/.test(tok))return[[card(tok.slice(0,2)),card(tok.slice(2))]];
  const a=RANKS.indexOf(tok[0]),b=RANKS.indexOf(tok[1]),t=tok[2];
  for(let s1=0;s1<4;s1++)for(let s2=0;s2<4;s2++){
    if(a===b){if(s2<=s1)continue}else{if(t==='s'&&s1!==s2)continue;if(t==='o'&&s1===s2)continue}
    out.push([a*4+s1,b*4+s2])}
  return out}
function range(spec,dead=[]){const D=new Set(dead),m=new Map();
  for(const raw of spec.trim().split(/\s+/)){const[tok,wt]=raw.split(':');const w=wt===undefined?1:+wt;
    for(const c of combosOfToken(tok)){if(D.has(c[0])||D.has(c[1]))continue;const k=Math.min(...c)+','+Math.max(...c);m.set(k,{c,w})}}
  return[...m.values()]}
// ---- opponent class on a given board (for call decisions) ----
function oppClass(h,board){
  const s=score(h,board),cat=s>>20,bs=board.length>=5?ev(board):-1;
  if(board.length>=5&&s<=bs)return'air';
  const hr=[cr(h[0]),cr(h[1])],k1=s>>16&15,k2=s>>12&15;
  if(cat>=4)return'strong';
  if(cat===3)return hr.includes(k1)?'strong':'air';
  if(cat===2)return(hr.includes(k1)||hr.includes(k2))?'strong':'air';
  const br=[...new Set(board.map(cr))].sort((a,b)=>b-a);
  if(cat===1){if(!hr.includes(k1))return hr.includes(12)?'ace':'air';
    if(k1>br[0])return'top';if(k1===br[0])return'top';if(k1>=br[1])return'mid';return'weak'}
  return hr.includes(12)?'ace':'air'}
function hasFlushDraw(h,board){const sc=[0,0,0,0];[...h,...board].forEach(c=>sc[cs(c)]++);for(let s=0;s<4;s++)if(sc[s]===4&&(cs(h[0])===s||cs(h[1])===s))return true;return false}
// call probability vs a bet of fraction f of the pot (river)
function callProb(cls,f){
  switch(cls){case'strong':return 1;
    case'top':return f<=.8?1:f<=1.2?.45:.15;
    case'mid':return f<=.4?.85:f<=.8?.35:.05;
    case'weak':return f<=.4?.4:f<=.8?.1:0;
    case'ace':return f<=.4?.2:0;default:return 0}}
// ---- equity of hero vs a weighted range, exact over remaining board cards (MC when many) ----
function equity(hero,board,rng,mc=0){const dead=new Set([...hero,...board]);let W=0,E=0;
  const need=5-board.length;const deck=[];for(let c=0;c<52;c++)if(!dead.has(c))deck.push(c);
  if(mc){for(let i=0;i<mc;i++){const o=rng[Math.random()*rng.length|0];
      const used=new Set([...dead,...o.c]);const b=board.slice();while(b.length<5){const x=Math.random()*52|0;if(!used.has(x)){used.add(x);b.push(x)}}
      const a=score(hero,b),v=score(o.c,b);E+=o.w*(a>v?1:a===v?.5:0);W+=o.w}return E/W}
  for(const o of rng){const d2=deck.filter(c=>c!==o.c[0]&&c!==o.c[1]);
    const runs=need===0?[[]]:need===1?d2.map(c=>[c]):need===2?d2.flatMap((c,i)=>d2.slice(i+1).map(e=>[c,e])):null;
    let e=0;for(const r of runs){const b=[...board,...r];const a=score(hero,b),v=score(o.c,b);e+=a>v?1:a===v?.5:0}
    E+=o.w*e/runs.length;W+=o.w}
  return E/W}
// ---- river: hero acts first-to-act after villain checks; villain never raises ----
function riverActions(hero,board,rng,pot,eff,sizes,checkW){
  let R=rng.filter(o=>!board.includes(o.c[0])&&!board.includes(o.c[1]));
  if(checkW)R=R.map(o=>({c:o.c,w:o.w*checkW(oppClass(o.c,board))})).filter(o=>o.w>0);let W=0;R.forEach(o=>W+=o.w);
  const sh=R.map(o=>{const a=score(hero,board),v=score(o.c,board);return a>v?1:a===v?.5:0});
  const cls=R.map(o=>oppClass(o.c,board));
  const res=[];
  let e=0;R.forEach((o,i)=>e+=o.w*sh[i]*pot);res.push({a:'check',ev:e/W});
  for(const[lab,f]of sizes){const s=Math.min(eff,f==='allin'?eff:Math.round(pot*f*100)/100);const fr=s/pot;
    let v=0,fold=0;R.forEach((o,i)=>{const q=callProb(cls[i],fr);v+=o.w*((1-q)*pot+q*(sh[i]*(pot+2*s)-s));fold+=o.w*(1-q)});
    res.push({a:'bet',lab,size:s,ev:v/W,fold:fold/W})}
  return{res,W}}
// hero facing a river bet from the villain's betting range
function facingBet(hero,board,rng,pot,bet){let W=0,v=0,win=0;
  for(const o of rng){if(board.includes(o.c[0])||board.includes(o.c[1]))continue;const a=score(hero,board),b=score(o.c,board);const s=a>b?1:a===b?.5:0;
    v+=o.w*(s*(pot+bet)-(1-s)*bet);win+=o.w*s;W+=o.w}
  return{call:v/W,win:win/W}}
module.exports={card,cards,range,equity,riverActions,facingBet,oppClass,callProb,hasFlushDraw,score,cr,cs,RANKS};

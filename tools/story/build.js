const E=require('./engine.js');const fs=require('fs');
const{cards,range,equity,riverActions,facingBet}=E;
const T=(potBB)=>({perfect:Math.max(.15,.03*potBB),two:Math.max(1.5,.15*potBB),one:Math.max(5,.5*potBB)});
const stars=(loss,potBB)=>{const t=T(potBB);return loss<=t.perfect?3:loss<=t.two?2:loss<=t.one?1:0};
function finish(node,opts,potBB){const best=Math.max(...opts.map(o=>o.ev));
  opts.forEach(o=>{o.loss=+(best-o.ev).toFixed(2);o.stars=stars(o.loss,potBB);o.ev=+o.ev.toFixed(2)});node.options=opts;node.best=opts.find(o=>o.ev===Math.max(...opts.map(x=>x.ev))).id;return node}
const st=[];

/* ---------- 1~3: preflop opens (range chart) ---------- */
st.push({id:1,title:'첫 오픈',tag:'프리플랍',intro:'6인 테이블, 모두 100BB. 당신은 첫 번째로 행동하는 UTG입니다. 뒤에 다섯 명이 남아 있어요.',
 nodes:{a:{type:'chart',pos:'UTG',hero:'Ad Qc',board:'',potBB:1.5,toCallBB:1,situ:'아무도 액션하지 않았습니다. 무엇을 할까요?',
  options:[{id:'fold',label:'폴드',stars:2,why:'AQo는 UTG에서도 상위 약 3% 안에 드는 핸드라 접기엔 아깝습니다.'},
           {id:'limp',label:'콜(림프) 1BB',stars:1,why:'림프는 주도권을 버리고, 뒤에서 레이즈가 오면 애매한 상황만 남깁니다.'},
           {id:'raise',label:'레이즈 2.5BB',stars:3,why:'앞이 다 폴드한 상황에서 강한 핸드는 먼저 레이즈해 팟을 가져가거나 키웁니다.'}],
  best:'raise',outcome:{raise:'BTN과 BB가 폴드하고 CO만 콜. 좋은 시작입니다.',fold:'다음 핸드를 기다립니다. 상위 3% 핸드를 버렸어요.',limp:'뒤에서 BTN이 5BB로 레이즈. 당신은 애매하게 콜하고 아웃오브포지션으로 끌려갑니다.'}}},start:'a'});
st.push({id:2,title:'참는 법',tag:'프리플랍',intro:'같은 UTG 자리. 이번엔 그림 카드가 들어왔지만 짝이 안 맞습니다.',
 nodes:{a:{type:'chart',pos:'UTG',hero:'Kc 9d',board:'',potBB:1.5,toCallBB:1,situ:'아무도 액션하지 않았습니다. 무엇을 할까요?',
  options:[{id:'fold',label:'폴드',stars:3,why:'K9o는 UTG 오픈 범위(상위 약 15%) 밖입니다. 뒤 다섯 명 중 누군가 더 좋은 K나 A를 들고 있을 확률이 높아요.'},
           {id:'limp',label:'콜(림프) 1BB',stars:1,why:'약한 핸드로 림프하면 주도권도 없고 도미네이트 당하기 쉽습니다.'},
           {id:'raise',label:'레이즈 2.5BB',stars:2,why:'버튼이라면 좋은 오픈이지만, UTG에선 콜을 받으면 KQ·KJ·AK 같은 패에 지배당합니다.'}],
  best:'fold',outcome:{fold:'참았습니다. 이 핸드에서 CO가 KJ로 오픈했어요.',raise:'CO가 3벳. 폴드하면 2.5BB를 잃습니다.',limp:'BTN이 레이즈하고 당신은 끌려다닙니다.'}}},start:'a'});
st.push({id:3,title:'버튼의 특권',tag:'프리플랍',intro:'이번엔 버튼(BTN). 앞에서 모두 폴드했고 블라인드 두 명만 남았습니다.',
 nodes:{a:{type:'chart',pos:'BTN',hero:'7s 6s',board:'',potBB:1.5,toCallBB:1,situ:'UTG, HJ, CO 모두 폴드. 무엇을 할까요?',
  options:[{id:'fold',label:'폴드',stars:2,why:'버튼은 포스트플랍에서 항상 마지막에 행동하는 가장 유리한 자리입니다. 76s 같은 수트 커넥터는 여기서 열어야 이익입니다.'},
           {id:'limp',label:'콜(림프) 1BB',stars:1,why:'버튼 림프는 블라인드를 훔칠 기회를 버립니다.'},
           {id:'raise',label:'레이즈 2.5BB',stars:3,why:'버튼 오픈 범위는 상위 40%를 넘습니다. 블라인드가 자주 폴드하고, 콜해도 포지션이 있어요.'}],
  best:'raise',outcome:{raise:'SB 폴드, BB 폴드. 블라인드 1.5BB를 가져옵니다.',fold:'블라인드를 훔칠 기회를 넘겼습니다.',limp:'BB가 체크하고 3명이 작은 팟을 봅니다.'}}},start:'a'});

/* ---------- 4: preflop shove call ---------- */
{const hero=cards('As 8d');const ORDER='AA KK QQ JJ TT 99 AKs AQs 88 AJs AQo AKo KQs ATs 77 KJs AJo A9s KTs A8s KQo ATo QJs K9s KTo 66 KJo A5s JTs A9o A7s QTs A4s A6s A8o QJo Q9s 55 K8s A3s K7s A7o QTo JTo A2s K9o J9s A5o A6o K6s Q8s Q9o J8s T9s K5s A4o K4s J9o T8s 44 K8o Q7s A2o A3o K6o K3s T9o 98s Q5s Q6s J7s K2s K7o K5o Q8o T7s Q4s Q7o 33 97s J8o Q3s 87s J5s T8o K4o Q2s J6s Q6o 98o T5s Q4o J7o T6s 86s 96s Q5o K3o J4s J3s 76s 22 K2o J2s 97o T4s 75s T7o 87o'.split(' ');
 let n=0;const pick=[];for(const k of ORDER){if(n/1326>=.45)break;pick.push(k);n+=k.length===2?6:k[2]==='s'?4:12}
 const rng=range(pick.join(' '),hero);const eq=equity(hero,[],rng,400000);
 const pot=16,call=14;const node={type:'allin',pos:'BB',hero:'As 8d',board:'',potBB:pot,toCallBB:call,
  situ:'모두 15BB 남은 상태. 앞이 다 폴드하고 SB가 15BB 올인했습니다. 당신은 BB(1BB 냄). 14BB를 더 내고 콜할까요?',
  oppRange:`SB 올인 범위 · 상위 약 45% (${pick.slice(0,6).join(', ')} … ${pick.slice(-4).join(', ')})`,eq};
 finish(node,[{id:'fold',label:'폴드',ev:0},{id:'call',label:'콜 14BB',ev:eq*30-call}],pot);
 node.outcome={call:'SB는 K♣9♥. 보드 Q♦7♣4♠ 2♥ J♦, A-하이로 이깁니다. 결과보다 콜 결정이 맞았다는 게 중요해요.',fold:'SB가 K♣9♥를 보여줍니다. 넓은 올인 범위엔 A8o가 앞서는 경우가 많아요.'};
 node.lesson=`A8o의 승률은 ${(eq*100).toFixed(1)}%, 콜에 필요한 승률은 14 ÷ 30 = 46.7%.`;
 st.push({id:4,title:'올인을 받을 때',tag:'팟 오즈',intro:'토너먼트 후반처럼 스택이 짧아진 상황. SB가 당신의 BB를 향해 올인합니다.',nodes:{a:node},start:'a'})}

/* ---------- 5: flop draw all-in ---------- */
{const hero=cards('Ah 5h'),board=cards('Kh 8h 2c');
 const rng=range('KK 88 22 K8s AK KQ KJ KT:0.7 K9s:0.5 QhJh ThJh Th9h Qh9h 9h7h AA:0.3 QQ:0.3',[...hero,...board]);
 const eq=equity(hero,board,rng);const pot=8.5,call=24.5;
 const node={type:'allin',pos:'CO',hero:'Ah 5h',board:'Kh 8h 2c',potBB:pot,toCallBB:call,
  situ:'스택 30BB. 당신이 CO에서 2.5BB 오픈, BB만 콜. 플랍에서 3BB 벳했는데 BB가 남은 27.5BB 올인. 24.5BB를 더 내고 콜할까요?',
  oppRange:'BB 체크-올인 범위 · 셋(KK·88·22), 투페어 K8, 탑페어(AK·KQ·KJ·KT·K9), 더 낮은 하트 드로우(Q♥J♥·J♥T♥·T♥9♥ 등)',eq};
 finish(node,[{id:'fold',label:'폴드',ev:0},{id:'call',label:'콜 24.5BB',ev:eq*(pot+27.5+27.5-3)-call}],pot);
 node.outcome={call:'BB는 K♠Q♦. 턴 3♠, 리버 J♥ — 넛 플러시 완성. 이번엔 이겼지만 지는 경우도 많은 동전 던지기에 가까운 콜이었어요.',fold:'BB가 K♠Q♦를 보여줍니다. 넛 플러시 드로우 + A 오버카드는 생각보다 승률이 높습니다.'};
 node.lesson=`넛 플러시 드로우 + A 오버카드의 승률 ${(eq*100).toFixed(1)}%, 필요한 승률 24.5 ÷ 60.5 = 40.5%.`;
 st.push({id:5,title:'드로우의 값',tag:'팟 오즈',intro:'플랍에서 넛 플러시 드로우를 잡았는데, 상대가 올인으로 맞섭니다.',nodes:{a:node},start:'a'})}

/* ---------- 6: turn gutshot facing shove ---------- */
{const hero=cards('Jc Tc'),board=cards('Qd 8s 3c 2h');
 const rng=range('AQ KQ QJ:0.6 QT:0.4 Q9s QQ 88 33 Q8s',[...hero,...board]);const eq=equity(hero,board,rng);const pot=12,call=12;
 const node={type:'allin',pos:'BTN',hero:'Jc Tc',board:'Qd 8s 3c 2h',potBB:pot,toCallBB:call,
  situ:'턴까지 왔고 팟은 12BB. 상대가 남은 12BB를 올인했습니다. 9가 나오면 스트레이트입니다.',
  oppRange:'상대 범위 · Q 원페어(AQ·KQ·QJ·QT·Q9s), 셋(QQ·88·33), 투페어 Q8s',eq};
 finish(node,[{id:'fold',label:'폴드',ev:0},{id:'call',label:'콜 12BB',ev:eq*(pot+24)-call}],pot);
 node.outcome={fold:'상대는 A♠Q♣. 리버 5♦ — 콜했다면 졌습니다.',call:'상대는 A♠Q♣. 리버 5♦, 스트레이트를 놓쳐 집니다.'};
 node.lesson=`거트샷 아웃 4장(9)뿐이라 승률 ${(eq*100).toFixed(1)}%, 필요한 승률 12 ÷ 36 = 33%. 아웃 × 2 ≈ 8%로 암산해도 됩니다.`;
 st.push({id:6,title:'거트샷의 함정',tag:'팟 오즈',intro:'스트레이트까지 한 장. 하지만 그 한 장이 몇 장이나 남았는지 세어 봐야 합니다.',nodes:{a:node},start:'a'})}

/* ---------- 7: thin value river ---------- */
{const hero=cards('As Jd'),board=cards('Jc 7d 4s 2h 9c');
 const rng=range('KJ QJ JT J8s 87s 76s A7s A7o:0.5 97s 99:0.3 88 TT 66 55 65s T8s:0.5 A4s',[...hero,...board]);
 const pot=14,eff=80;const{res}=riverActions(hero,board,rng,pot,eff,[['⅓팟',1/3],['⅔팟',2/3],['팟',1],['올인','allin']]);
 const opts=res.map(r=>r.a==='check'?{id:'check',label:'체크',ev:r.ev}:{id:'bet'+r.lab,label:`벳 ${r.lab} (${+r.size.toFixed(1)}BB)`,ev:r.ev,fold:r.fold});
 const node={type:'river',pos:'BTN',hero:'As Jd',board:'Jc 7d 4s 2h 9c',potBB:pot,toCallBB:0,
  situ:'BB가 플랍·턴에서 체크-콜했고 리버에서도 체크했습니다. 팟 14BB, 남은 스택 80BB. 탑페어 탑키커예요.',
  oppRange:'BB 체크-콜 범위 · 약한 J(KJ·QJ·JT), 7 페어(A7·87s·76s), 포켓페어(88·TT·66·55), 리버에 맞은 투페어·스트레이트(J8s·97s·T8s) 조금'};
 finish(node,opts,pot);
 node.outcome={check:'BB는 Q♠J♠. 쇼다운으로 14BB를 가져가지만, 벳했다면 더 받을 수 있었어요.'};
 node.outcomeDefault='BB는 Q♠J♠로 콜. 더 약한 J에게서 밸류를 받아냈습니다.';
 node.lesson='상대가 콜할 수 있는 더 약한 패가 충분하면 "얇은 밸류 벳"이 체크보다 낫습니다. 너무 크게 걸면 약한 패가 다 도망가요.';
 st.push({id:7,title:'얇은 밸류',tag:'밸류 벳',intro:'리버까지 왔고 아마 이기고 있습니다. 문제는 "얼마나 더 받아낼 수 있나"예요.',nodes:{a:node},start:'a'})}

/* ---------- 8: bluff catch ---------- */
{const hero=cards('Ad Td'),board=cards('Ts 9s 4d 2c Kh');
 const rng=range('AK:0.5 KQs:0.5 KT:0.5 K9s:0.5 QJs:0.5 TT:0.3 99:0.3 44:0.3 AsQs As5s As4s Qs8s Js8s 8s7s 7s6s AsJs',[...hero,...board]);
 const pot=20,bet=15;const r=facingBet(hero,board,rng,pot,bet);
 const node={type:'facing',pos:'BB',hero:'Ad Td',board:'Ts 9s 4d 2c Kh',potBB:pot,toCallBB:bet,
  situ:'BTN이 플랍·턴에 벳했고 리버 K에서 15BB(¾팟)를 겁니다. 팟 20BB. 당신은 T 페어 A 키커. 콜할까요?',
  oppRange:'BTN 리버 벳 범위 · 밸류(AK·KQs·KT·K9s, 셋, QJs 스트레이트) + 놓친 스페이드 드로우 블러프(A♠Q♠·A♠5♠·Q♠8♠·J♠8♠·8♠7♠·7♠6♠ 등)',eq:r.win};
 finish(node,[{id:'fold',label:'폴드',ev:0},{id:'call',label:'콜 15BB',ev:r.call}],pot);
 node.outcome={call:'BTN은 J♠8♠ — 스트레이트와 플러시를 다 놓친 블러프였습니다.',fold:'BTN이 J♠8♠를 보여주며 웃습니다. 블러프였어요.'};
 node.lesson=`콜에 필요한 승률은 15 ÷ 50 = 30%. 상대 범위에 놓친 스페이드 드로우가 많아서 T 페어가 ${(r.win*100).toFixed(0)}%를 이깁니다. `+(r.win>=.3?'그래서 콜이 이득이에요.':'그래도 30%엔 못 미쳐 폴드가 낫습니다.');
 st.push({id:8,title:'블러프 캐치',tag:'리버 콜',intro:'드로우가 많던 보드에서 리버는 블랭크. 상대가 크게 겁니다. 정말 강한 걸까요?',nodes:{a:node},start:'a'})}

/* ---------- 9: river bluff ---------- */
{const hero=cards('6s 5s'),board=cards('As Kd 8s 2h Jd');
 const rng=range('A2o:0.5 A3o:0.5 A4o:0.5 A5o:0.3 K9s KTs:0.5 K5s:0.5 Q8s:0.3 98s 87s 88:0.3 77 66 55 44 33 22 T9s J9s:0.4 QT:0.3 K8s:0.3',[...hero,...board]);
 const pot=9,eff=40;const{res}=riverActions(hero,board,rng,pot,eff,[['½팟',.5],['¾팟',.75],['팟',1]]);
 const opts=res.map(r=>r.a==='check'?{id:'check',label:'체크',ev:r.ev}:{id:'bet'+r.lab,label:`벳 ${r.lab} (${+r.size.toFixed(1)}BB)`,ev:r.ev,fold:r.fold});
 const node={type:'river',pos:'BTN',hero:'6s 5s',board:'As Kd 8s 2h Jd',potBB:pot,toCallBB:0,
  situ:'플랍에서 c-벳, BB 콜. 턴은 둘 다 체크. 리버에서 BB가 또 체크했습니다. 팟 9BB. 당신은 6-하이로 거의 못 이깁니다.',
  oppRange:'BB 범위 · 턴에 체크로 약함을 보임. 약한 A(A2~A5), K 페어, 8 페어(98s·87s), 작은 포켓페어(22~77) 위주'};
 finish(node,opts,pot);
 node.outcome={check:'BB가 7♣7♥를 보여줍니다. 6-하이로는 질 수밖에 없어요.'};
 node.outcomeDefault='BB가 한참 고민하다 7♣7♥를 접습니다. 블러프 성공.';
 node.lesson='체크하면 거의 다 지는 패는, 상대가 충분히 폴드할 크기로 블러프하는 게 이득입니다. 상대가 턴에 체크한 건 강한 패가 적다는 신호예요.';
 st.push({id:9,title:'놓친 드로우의 기회',tag:'블러프',intro:'플러시 드로우를 놓쳤습니다. 이대로 포기할까요, 아니면 이야기를 만들까요?',nodes:{a:node},start:'a'})}

/* ---------- 10: BOSS — Moneymaker vs Farha, 2003 WSOP Main Event ---------- */
{const BBc=40000;const hero=cards('Ks 7h'),turnB=cards('9s 2d 6s 8s'),river=E.card('3h');
 const spec='A9 K9 Q9 J9 T9 98 96s 92s A8 K8 Q8:0.5 87s 88 66 22 T7:0.6 75s 7s5s AsQs AsJs AsTs QsJs JsTs Ts7s As4s As3s 99:0.5';
 const rngT=range(spec,[...hero,...turnB]);
 const potT=210000/BBc,betT=300000/BBc,heroStack=4500000/BBc,villStack=3600000/BBc;
 // turn raise response (calls with made hands / good draws)
 const turnCall=o=>{const cls=E.oppClass(o.c,turnB),fd=E.hasFlushDraw(o.c,turnB);if(cls==='strong')return 1;if(cls==='top')return fd?1:.8;if(cls==='mid')return fd?.8:.3;return fd?.5:0};
 const deck=[];for(let c=0;c<52;c++)if(!hero.includes(c)&&!turnB.includes(c))deck.push(c);
 const RIVER_SIZES=[['½팟',.5],['올인','allin']];
 // when Farha checks the river, his strong hands are mostly gone (they would bet); medium hands check
 const CHECKW=cls=>cls==='strong'?.35:1;
 const BETP=cls=>cls==='strong'?.65:0;
 function lineEV(rng,pot,eff){let tot=0,W=0;for(const r of deck){const R=rng.filter(o=>o.c[0]!==r&&o.c[1]!==r);if(!R.length)continue;let w=0;R.forEach(o=>w+=o.w);
   const b=[...turnB,r],hs=E.score(hero,b),heroStrong=E.oppClass(hero,b)==='strong';
   // part 1: Farha bets ¾ pot with some strong hands; hero calls only with a made straight/flush
   let vb=0;for(const o of R){const p=BETP(E.oppClass(o.c,b));if(!p)continue;const bet=Math.min(eff,.75*pot);const vs=E.score(o.c,b);const sh=hs>vs?1:hs===vs?.5:0;
     vb+=o.w*p*(heroStrong?sh*(pot+bet)-(1-sh)*bet:0)}
   // part 2: Farha checks; hero picks the best action against the checking range
   let wc=0;R.forEach(o=>wc+=o.w*CHECKW(E.oppClass(o.c,b)));
   const{res}=E.riverActions(hero,b,R,pot,eff,RIVER_SIZES,CHECKW);
   tot+=vb+wc*Math.max(...res.map(x=>x.ev));W+=w}return tot/W}
 const callPot=potT+2*betT;
 const evCall=-betT+lineEV(rngT,callPot,villStack-betT);
 function raiseEV(to){let fold=0,W=0;const called=[];rngT.forEach(o=>{const q=to>=villStack?Math.max(0,turnCall(o)-.3):turnCall(o);W+=o.w;fold+=o.w*(1-q);if(q>0)called.push({c:o.c,w:o.w*q})});
   const pf=fold/W;let cw=0;called.forEach(o=>cw+=o.w);
   let v;if(to>=villStack){v=0;let ws=0;called.forEach(o=>{ws+=o.w});const eqc=called.length?E.equity(hero,turnB,called):0;v=eqc*(potT+betT+2*villStack-betT)-(villStack)}
   else v=-to+lineEV(called,potT+betT+to,villStack-to);
   return{ev:pf*(potT+betT)+(1-pf)*v,fold:pf,called}}
 const r800=raiseEV(800000/BBc),rAll=raiseEV(villStack);
 const turn={type:'tree',pos:'BTN',hero:'Ks 7h',board:'9s 2d 6s 8s',potBB:potT+betT,toCallBB:betT,unit:BBc,
  situ:'플랍 9♠2♦6♠은 둘 다 체크. 턴 8♠에서 파르하가 팟(210,000)보다 큰 300,000을 벳합니다. 당신은 K♠ 플러시 드로우 + 양방 스트레이트 드로우(5 또는 10)를 들고 있어요.',
  oppRange:'파르하의 턴 벳 범위(가정) · 9 페어(A9~T9), 투페어(98·96s·92s), 8 페어, 셋, 스트레이트(T7·75s), 플러시·스페이드 드로우',
  eq:E.equity(hero,turnB,rngT)};
 finish(turn,[{id:'fold',label:'폴드',ev:0},{id:'call',label:'콜 300,000',ev:evCall,next:'rc'},{id:'raise',label:'레이즈 800,000',ev:r800.ev,fold:r800.fold,next:'rr'},{id:'allin',label:'올인 3,600,000',ev:rAll.ev,fold:rAll.fold}],potT+betT);
 turn.outcome={fold:'카드를 던집니다. 파르하는 Q♠9♥를 보여주지 않고 팟을 가져갑니다. 역사에 남을 장면은 일어나지 않았어요.',allin:'파르하가 한참 고민하다 콜. 리버 3♥ — 둘 다 놓쳤고 Q♠9♥의 9 페어가 이깁니다.'};
 turn.lesson=`플러시 드로우 + 양방 스트레이트 드로우는 아웃이 15장 안팎이라 이 범위 상대 승률 ${(turn.eq*100).toFixed(0)}%. 리버에서 블러프할 수 있다는 점도 콜·레이즈의 가치를 높입니다.`;
 const mk=(id,rng,pot,eff,prefix)=>{const b=[...turnB,river];const R=rng.filter(o=>o.c[0]!==river&&o.c[1]!==river);
   const{res}=E.riverActions(hero,b,R,pot,eff,[['½팟',.5],['올인','allin']],CHECKW);
   const opts=res.map(r=>r.a==='check'?{id:'check',label:'체크',ev:r.ev}:{id:r.lab==='올인'?'allin':'half',label:r.lab==='올인'?`올인 ${(r.size*BBc).toLocaleString('ko-KR')}`:`벳 ½팟 ${(r.size*BBc).toLocaleString('ko-KR')}`,ev:r.ev,fold:r.fold});
   const n={type:'river',pos:'BTN',hero:'Ks 7h',board:'9s 2d 6s 8s 3h',potBB:pot,toCallBB:0,unit:BBc,
    situ:`${prefix} 리버 3♥. 스트레이트도 플러시도 놓쳤습니다. K-하이. 파르하가 체크합니다. 팟 ${(pot*BBc).toLocaleString('ko-KR')}.`,
    oppRange:'파르하의 범위 · 턴에 벳하고 '+(id==='rr'?'레이즈에 콜':'콜을 받은')+' 패들. 9 페어와 8 페어, 드로우를 놓친 패가 섞여 있음'};
   finish(n,opts,pot);
   n.outcome={check:'파르하가 Q♠9♥를 보여줍니다. 9 페어. K-하이로 집니다.',allin:'파르하가 한참 동안 당신을 바라보다가 Q♠9♥를 접습니다. 실제 2003년의 그 장면입니다.',half:'파르하가 Q♠9♥로 콜합니다. 9 페어는 반 팟 정도엔 콜하기 쉬워요.'};
   n.lesson='K-하이로 체크하면 거의 모든 패에 집니다. 상대가 9 페어 정도의 "중간 패"를 들고 있을 때는, 작은 벳보다 아주 큰 벳이 접게 만들기 쉽습니다.';
   return n};
 const rc=mk('rc',rngT,callPot,villStack-betT,'턴에서 콜했습니다.');
 const rr=mk('rr',r800.called,potT+betT+800000/BBc,villStack-800000/BBc,'턴에서 800,000으로 레이즈했고 파르하가 콜했습니다.');
 st.push({id:10,title:'세기의 블러프',tag:'보스 · 실제 핸드',real:true,
  intro:'2003년 WSOP 메인 이벤트 헤즈업. 온라인 예선으로 올라온 회계사 크리스 머니메이커(당신)가 프로 새미 파르하와 맞섭니다. 블라인드 20,000/40,000, 앤티 5,000. 당신 4,600,000, 파르하 약 3,700,000. 버튼에서 K♠7♥로 100,000 레이즈, 파르하 콜.',
  real_play:'실제로 머니메이커는 턴에서 800,000으로 레이즈했고 파르하가 콜, 리버 3♥에서 파르하 체크 후 올인했습니다. 파르하는 Q♠9♥(9 페어)를 접었고, 머니메이커는 이후 우승하며 "포커 붐"을 일으켰습니다.',
  source:'https://www.pokernews.com/strategy/analyzing-moneymaker-bluff-of-the-century-against-farha-35218.htm',
  nodes:{a:turn,rc,rr},start:'a'})}

const SHOW={4:16,5:36,6:24,8:35};for(const x of st)if(SHOW[x.id])x.nodes.a.showPot=SHOW[x.id];
fs.writeFileSync(__dirname+'/chapter1.json',JSON.stringify({chapter:1,title:'첫 테이블',stages:st}));
for(const s of st)for(const[k,n]of Object.entries(s.nodes))console.log(s.id,k,n.type,'best',n.best,(n.options||[]).map(o=>`${o.id}:${o.ev??''}/${o.stars}`).join(' '),n.eq?('eq '+(n.eq*100).toFixed(1)):'');

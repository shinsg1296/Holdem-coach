"""Build app/src/main/assets/index.html from the claude.ai artifact page (holdem-live.html).

The artifact asks Claude through claude.ai and stores reports in the artifact's database.
In the Android app those become: direct Anthropic API calls with the user's own key, and
reports kept on the phone that can be shared or copied.

usage: python3 tools/build_web.py path/to/holdem-live.html
"""
import sys, pathlib

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
out = pathlib.Path(__file__).resolve().parent.parent / "app/src/main/assets/index.html"
s = src

def R(old, new):
    global s
    if old not in s:
        sys.exit("pattern not found: " + old[:80])
    s = s.replace(old, new, 1)

# ---- page head (the artifact host normally adds these) ----
s = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
     '<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>\n') + s
R("<div class=\"wrap\">", "</head><body>\n<div class=\"wrap\">")
s = s.rstrip() + "\n</body></html>\n"

# ---- Claude: direct API with the user's key ----
R("let sampleFn=null,sampleState='loading',chatCtl=null,chatBusy=false;\n"
  "(async()=>{try{sampleFn=await window.claude?.use?.('sample')}catch(e){sampleFn=null}sampleState=sampleFn?'ready':'off';renderChat()})();",
  r"""let sampleState='ready',chatCtl=null,chatBusy=false;
const LS={get:(k,d='')=>{try{return localStorage.getItem(k)??d}catch(e){return d}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
const MODELS=[['claude-sonnet-5-5','Sonnet 5.5 · 기본'],['claude-haiku-4-5-20251001','Haiku 4.5 · 빠르고 저렴'],['claude-opus-5-5','Opus 5.5 · 가장 깊이 있게']];
async function sampleFn(input,opts={}){
  const key=LS.get('apiKey').trim();if(!key)throw{code:'no_key'};
  const turns=typeof input==='string'?[{role:'user',content:input}]:input;const msgs=[];
  for(const t of turns){const last=msgs[msgs.length-1];if(last&&last.role===t.role)last.content+='\n\n'+t.content;else msgs.push({role:t.role,content:t.content})}
  let res;
  try{res=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',signal:opts.signal,
    headers:{'content-type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true'},
    body:JSON.stringify({model:LS.get('model',MODELS[0][0]),max_tokens:1500,stream:true,messages:msgs})})}
  catch(e){if(opts.signal?.aborted)throw{code:'cancelled'};throw{code:'network'}}
  if(!res.ok){let m='';try{m=(await res.json())?.error?.message||''}catch(e){}
    throw{code:res.status===401||res.status===403?'auth_error':res.status===429?'rate_limited':res.status===529||res.status>=500?'upstream_error':'bad_request',message:m}}
  const rd=res.body.getReader(),dec=new TextDecoder();let buf='',text='';
  try{for(;;){const{done,value}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;
    while((i=buf.indexOf('\n'))>=0){const line=buf.slice(0,i).trim();buf=buf.slice(i+1);if(!line.startsWith('data:'))continue;
      let ev;try{ev=JSON.parse(line.slice(5))}catch(e){continue}
      if(ev.type==='content_block_delta'&&ev.delta?.type==='text_delta'){text+=ev.delta.text;opts.onText?.({text,delta:ev.delta.text})}
      else if(ev.type==='error')throw{code:'upstream_error',message:ev.error?.message}}}}
  catch(e){if(opts.signal?.aborted)throw{code:'cancelled',text};throw{code:e?.code||'network',text}}
  if(!text.trim())throw{code:'empty_completion'};return{text,truncated:false}}""")
R("const ERRS={", "const ERRS={no_key:'질문하려면 위쪽 \\'설정\\'에서 Anthropic API 키를 넣어 주세요.',auth_error:'API 키가 맞지 않습니다. 설정에서 키를 확인해 주세요.',network:'인터넷 연결을 확인해 주세요.',bad_request:'요청이 거절됐습니다. 설정에서 모델을 바꿔 보세요.',")
R("- 엔진이 틀렸다고 판단되면, 해설 아래 '이 해설이 이상해요'로 신고하면 앱을 만든 Claude 대화창에서 엔진을 고칠 수 있다고 안내하라.",
  "- 엔진이 틀렸다고 판단되면, 해설 아래 '이 해설이 이상해요'로 신고한 뒤 앱 위쪽 '설정 → 신고 목록'에서 공유해 앱을 만든 Claude 대화창에 붙여넣으면 엔진을 고칠 수 있다고 안내하라.")

# ---- reports: kept on the phone ----
R("let dbRef=null;(async()=>{try{dbRef=await window.claude?.use?.('db')}catch(e){dbRef=null}renderChat()})();",
  r"""const REP_KEY='holdem-reports-v1';
const loadReports=()=>{try{return JSON.parse(localStorage.getItem(REP_KEY))||[]}catch(e){return[]}};
const dbRef={collection:()=>({add:async d=>{const a=loadReports();a.push(d);try{localStorage.setItem(REP_KEY,JSON.stringify(a))}catch(e){throw{code:'storage'}}renderSettings()}})};""")
R('신고했습니다. Claude 대화창에서 "신고한 해설 확인해줘"라고 하면 엔진을 고칩니다.',
  "신고를 저장했습니다. 위쪽 '설정 → 신고 목록'에서 공유하거나 복사해 Claude에게 보내면 엔진을 고칠 수 있어요.")

# ---- settings panel ----
R("  <div class=\"meta\" id=\"meta\"></div>",
  """  <div class="setrow"><button class="link" id="setBtn" aria-expanded="false" aria-controls="settings">설정 · 신고 목록</button></div>
  <section class="settings" id="settings" hidden>
    <div class="sgroup">
      <label for="keyIn">Anthropic API 키 <span class="ctx">해설에 대해 질문할 때만 쓰입니다. 이 폰에만 저장돼요.</span></label>
      <div class="ask"><input id="keyIn" type="password" autocomplete="off" placeholder="sk-ant-..."><button class="btn sendbtn" id="keySave" type="button">저장</button></div>
      <label for="modelSel">모델</label>
      <select id="modelSel"></select>
      <div class="ctx" id="keyMsg"></div>
    </div>
    <div class="sgroup">
      <div class="shead">신고 목록 <span id="repCount"></span></div>
      <div class="repbtns"><button class="btn sendbtn" id="repShare" type="button">공유</button><button class="btn sendbtn" id="repCopy" type="button">복사</button><button class="btn sendbtn" id="repClear" type="button">비우기</button></div>
      <div class="ctx" id="repMsg">공유하거나 복사한 내용을 Claude 대화창에 붙여넣고 "신고한 해설 확인해줘"라고 하면 엔진을 고칩니다.</div>
      <div id="repList" class="replist"></div>
    </div>
  </section>
  <div class="meta" id="meta"></div>""")
R("footer{font-size:11px;color:var(--muted)}", """footer{font-size:11px;color:var(--muted)}
.setrow{display:flex;justify-content:flex-end;margin-top:-6px}
.settings{border-radius:14px;padding:14px;background:var(--panel);border:1px solid var(--line);display:flex;flex-direction:column;gap:16px}
.sgroup{display:flex;flex-direction:column;gap:6px}
.sgroup label,.shead{font-size:13px;font-weight:700;display:flex;flex-direction:column;gap:2px}
.sgroup label .ctx{font-weight:400}
.settings select{font:inherit;font-size:14px;color:var(--ink);background:rgba(0,0,0,.3);border:1px solid var(--line);border-radius:10px;padding:9px 10px}
.repbtns{display:flex;gap:6px;flex-wrap:wrap}
.replist{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--muted)}
.replist div{border-top:1px solid var(--line);padding-top:4px}""")
R("/* ===== input ===== */", r"""/* ===== settings ===== */
function reportText(){const a=loadReports();if(!a.length)return'';
  return `[홀덤 실전 코치 · 신고 ${a.length}건]\n\n`+a.map((r,i)=>`### 신고 ${i+1} · 핸드 #${r.hand} · ${r.street} · ${r.engine}\n내 선택: ${r.choice} → ${({good:'좋은 선택',ok:'무난',bad:'실수'})[r.verdict]||r.verdict} / 엔진 추천: ${r.recommended}\n메모: ${r.note}\n\n${r.context}\n${r.chat?`\n[코치와의 대화]\n${r.chat}\n`:''}`).join('\n---\n\n')}
function renderSettings(){const a=loadReports();$('repCount').textContent=`${a.length}건`;
  $('repList').innerHTML=a.slice(-5).reverse().map(r=>`<div>핸드 #${r.hand} · ${r.street} · ${esc(r.choice)} · ${esc(String(r.note).slice(0,40))}</div>`).join('');
  ['repShare','repCopy','repClear'].forEach(id=>$(id).disabled=!a.length)}
{$('modelSel').innerHTML=MODELS.map(([v,l])=>`<option value="${v}">${l}</option>`).join('');$('modelSel').value=LS.get('model',MODELS[0][0]);
 $('keyIn').value=LS.get('apiKey');$('keyMsg').textContent=LS.get('apiKey')?'키가 저장돼 있습니다.':'키가 없으면 게임과 자동 해설만 쓸 수 있어요.';
 $('setBtn').onclick=()=>{const el=$('settings');el.hidden=!el.hidden;$('setBtn').setAttribute('aria-expanded',String(!el.hidden));if(!el.hidden)renderSettings()};
 $('keySave').onclick=()=>{LS.set('apiKey',$('keyIn').value.trim());$('keyMsg').textContent=$('keyIn').value.trim()?'저장했습니다.':'키를 지웠습니다.'};
 $('modelSel').onchange=()=>LS.set('model',$('modelSel').value);
 const copyText=t=>{if(window.Android?.copy){window.Android.copy(t);return}navigator.clipboard?.writeText(t).then(()=>{$('repMsg').textContent='복사했습니다.'},()=>{$('repMsg').textContent='복사하지 못했습니다.'})};
 $('repShare').onclick=()=>{const t=reportText();if(!t)return;if(window.Android?.share)window.Android.share(t);else if(navigator.share)navigator.share({text:t}).catch(()=>{});else copyText(t)};
 $('repCopy').onclick=()=>{const t=reportText();if(t)copyText(t)};
 let armed=false;$('repClear').onclick=()=>{if(!armed){armed=true;$('repClear').textContent='한 번 더 누르면 삭제';setTimeout(()=>{armed=false;$('repClear').textContent='비우기'},3000);return}
   armed=false;try{localStorage.removeItem(REP_KEY)}catch(e){}$('repClear').textContent='비우기';renderSettings()};
 renderSettings()}
/* ===== input ===== */""")
s = s.replace("본인 Claude 사용량이 쓰입니다", "설정에 넣은 API 키로 요금이 청구됩니다")

out.write_text(s, encoding="utf-8")
print("wrote", out, len(s), "bytes")

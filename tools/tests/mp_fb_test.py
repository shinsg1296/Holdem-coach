"""Real Firebase multiplayer test. Serves app/src/main/assets at the app's WebView origin
(https://appassets.androidplatform.net/assets/) and gives every player a separate browser context,
so each one is a different anonymous user going through the real security rules.
usage: python3 tools/tests/mp_fb_test.py [players=2] [iterations=400] [hands=5]"""
import asyncio,sys,random,json,mimetypes,pathlib
from playwright.async_api import async_playwright
ASSETS=pathlib.Path(__file__).resolve().parents[2]/'app'/'src'/'main'/'assets'
ORIGIN='https://appassets.androidplatform.net/assets/'
NP=int(sys.argv[1]) if len(sys.argv)>1 else 2
ITER=int(sys.argv[2]) if len(sys.argv)>2 else 400
HANDS=int(sys.argv[3]) if len(sys.argv)>3 else 5
async def serve(route):
    f=ASSETS/route.request.url[len(ORIGIN):].split('?')[0]
    if f.is_file(): await route.fulfill(body=f.read_bytes(),content_type=mimetypes.guess_type(f.name)[0] or 'application/octet-stream')
    else: await route.fulfill(status=404,body='')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();errs=[];logs=[];pages=[]
        for i in range(NP):
            ctx=await b.new_context(viewport={'width':400,'height':860})
            await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
            await ctx.route('**/fonts.googleapis.com/**',lambda r:r.abort())
            await ctx.route(ORIGIN+'**',serve)
            pg=await ctx.new_page();pg.on('pageerror',lambda e,i=i:errs.append(f'{i}:{e}'))
            pg.on('console',lambda m,i=i:logs.append(f'{i}:{m.text}') if m.type in('error','warning') else None)
            await pg.goto(ORIGIN+'index.html');await pg.wait_for_timeout(400)
            await pg.click('.mode[data-m="mp"]');await pg.fill('#mpName',['형','민수','지훈','영희'][i%4]+str(i));pages.append(pg)
        await pages[0].click('#mpNew');await pages[0].wait_for_selector('.mpcode',timeout=20000)
        code=await pages[0].locator('.mpcode').inner_text();print('room',code,'transport',await pages[0].evaluate('MP.net.kind'))
        for pg in pages[1:]:
            await pg.fill('#mpCodeIn',code);await pg.click('#mpJoinBtn');await pg.wait_for_timeout(1500)
        await pages[0].wait_for_timeout(1500)
        uids=[await pg.evaluate('MP.net&&MP.net.uid') for pg in pages];print('uids distinct',len(set(uids))==NP and None not in uids)
        await pages[0].click('#mpStart');await pages[0].wait_for_timeout(1500)
        acts=0;st={}
        for it in range(ITER):
            for pg in pages:
                if await pg.locator('#mpF').count():
                    r=random.random()
                    try:
                        if r<.15: await pg.click('#mpF',timeout=2000)
                        elif r<.3 and await pg.locator('#mpRopen:not([disabled])').count():
                            await pg.click('#mpRopen',timeout=2000);await pg.wait_for_timeout(60);n=await pg.locator('#mpMode .raisepanel .size').count();await pg.locator('#mpMode .raisepanel .size').nth(random.randrange(n)).click(timeout=2000);await pg.wait_for_timeout(50)
                            await pg.click('#mpR',timeout=2000);await pg.wait_for_timeout(30)
                            if await pg.locator('#mpR.armed').count(): await pg.click('#mpR',timeout=2000)
                        else: await pg.click('#mpC',timeout=2000)
                        acts+=1
                    except Exception: pass
                if await pg.locator('#mpRebuy').count():
                    try: await pg.click('#mpRebuy',timeout=2000)
                    except Exception: pass
            await pages[0].wait_for_timeout(250)
            st=json.loads(await pages[0].evaluate("JSON.stringify({h:MP.state.handNo,ph:MP.state.phase,stacks:MP.state.stacks,buy:MP.state.buyins,seats:(MP.state.seats||[]).map(s=>s.stack+s.total)})"))
            if st['h']>=HANDS and st['ph']=='result': break
        tot=sum(st['stacks'].values()) if st['ph']!='play' else sum(st['seats'])
        print('hands',st['h'],'phase',st['ph'],'actions',acts,'chips',tot,'expected',30000*sum(st['buy'].values()))
        g=pages[1]
        print('guest synced hand',await g.evaluate('MP.state&&MP.state.handNo'),'sees hole map',await g.evaluate("Object.keys(MP.state||{}).includes('hole')"),'own hand',(await g.evaluate('JSON.stringify(MP.hole)'))[:60])
        # security rules, checked from the guest: other player's cards, forging state, forging someone else's action
        print('rules',await g.evaluate("""async([code,host])=>{const db=firebase.database(),r={};
          const t=async(k,f)=>{try{await f();r[k]='ALLOWED'}catch(e){r[k]='denied'}};
          await t('read_host_hand',()=>db.ref('hands/'+code+'/'+host).get());
          await t('write_state',()=>db.ref('rooms/'+code+'/state/hack').set(1));
          await t('write_own_hand',()=>db.ref('hands/'+code+'/'+firebase.auth().currentUser.uid).set({cards:[0,1]}));
          await t('forge_action',()=>db.ref('rooms/'+code+'/actions').push({uid:host,a:'f'}));
          await t('take_host',()=>db.ref('rooms/'+code+'/meta/host').set(firebase.auth().currentUser.uid));
          return JSON.stringify(r)}""",[code,uids[0]]))
        print('ERR',errs[:5]);print('LOG',[l for l in logs if 'font' not in l.lower()][:8]);await b.close()
asyncio.run(main())

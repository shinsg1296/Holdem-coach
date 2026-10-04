import asyncio,sys,random,json
from playwright.async_api import async_playwright
URL=sys.argv[1];NP=int(sys.argv[2]) if len(sys.argv)>2 else 2
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':400,'height':860})
        await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1');localStorage.setItem('holdem-fbcfg','{\"local\":true}')}catch(e){}")
        await ctx.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        errs=[];pages=[]
        for i in range(NP):
            pg=await ctx.new_page();pg.on('pageerror',lambda e,i=i:errs.append(f'{i}:{e}'))
            await pg.goto(URL);await pg.wait_for_timeout(400)
            if i==0: await pg.evaluate("localStorage.removeItem('holdem-mp-store')")
            await pg.add_style_tag(content='[hidden]{display:none!important}')
            await pg.click('.mode[data-m="mp"]');await pg.fill('#mpName',['형','민수','지훈','영희'][i]);pages.append(pg)
        await pages[0].click('#mpNew');await pages[0].wait_for_timeout(400)
        code=await pages[0].locator('.mpcode').inner_text();print('room',code)
        for pg in pages[1:]:
            await pg.fill('#mpCodeIn',code);await pg.click('#mpJoinBtn');await pg.wait_for_timeout(300)
        await pages[0].wait_for_timeout(800)
        await pages[0].screenshot(path='/tmp/mp_lobby.png')
        await pages[0].click('#mpStart');await pages[0].wait_for_timeout(500)
        acts=0;shot=False
        for it in range(int(sys.argv[3]) if len(sys.argv)>3 else 500):
            for k,pg in enumerate(pages):
                if await pg.locator('#mpF').count():
                    r=random.random()
                    if r<.15: await pg.click('#mpF')
                    elif r<.3 and await pg.locator('#mpMode .raisepanel .size').count():
                        n=await pg.locator('#mpMode .raisepanel .size').count();await pg.locator('#mpMode .raisepanel .size').nth(random.randrange(n)).click();await pg.wait_for_timeout(50)
                        await pg.click('#mpR');await pg.wait_for_timeout(30)
                        if await pg.locator('#mpR.armed').count(): await pg.click('#mpR')
                    else: await pg.click('#mpC')
                    acts+=1
                    if not shot and acts>3:
                        await pg.screenshot(path='/tmp/mp_play.png');shot=True
                if await pg.locator('#mpRebuy').count(): await pg.click('#mpRebuy')
            await pages[0].wait_for_timeout(120)
            st=json.loads(await pages[0].evaluate("JSON.stringify({h:MP.state.handNo,ph:MP.state.phase,stacks:MP.state.stacks,buy:MP.state.buyins,seats:(MP.state.seats||[]).map(s=>s.stack+s.total)})"))
            if st['h']>=25 and st['ph']=='result': break
        tot=sum(st['stacks'].values()) if st['ph']!='play' else sum(st['seats'])
        print('dbg',await pages[0].evaluate("JSON.stringify({toAct:MP.state.toAct,left:MP.state.deadline-Date.now(),runout:MP.state.runout,street:MP.state.street,board:MP.state.board.length,running:MP.state.running,nextAt:MP.state.nextAt-Date.now()})"),await pages[1].evaluate("JSON.stringify({toAct:MP.state&&MP.state.toAct,me:mpMe(),h:MP.state&&MP.state.handNo})"))
        print('hands',st['h'],'phase',st['ph'],'actions',acts,'chips',tot,'expected',30000*sum(st['buy'].values()))
        leak=await pages[1].evaluate("JSON.stringify(Object.keys(MP.state||{}).includes('hole'))")
        mine=await pages[1].evaluate("JSON.stringify(MP.hole)")
        print('guest sees hole map:',leak,'guest own hand:',mine[:60])
        await pages[1].screenshot(path='/tmp/mp_guest.png')
        print('ERR',errs[:5]);await b.close()
asyncio.run(main())

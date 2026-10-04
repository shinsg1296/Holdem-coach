import asyncio,sys,random
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':400,'height':860});await pg.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' and 'Failed to load' not in m.text else None)
        await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.goto(URL);await pg.wait_for_timeout(600)
        await pg.add_style_tag(content='[hidden]{display:none!important}')
        await pg.check('#learnTgl')
        paused=0;raised=0;shot=False
        for i in range(160):
            if await pg.locator('#pRetry').count():
                paused+=1
                if not shot: await pg.screenshot(path='/tmp/ux_pause.png',full_page=True);shot=True
                await pg.click('#pGo' if paused%2 else '#pRetry');await pg.wait_for_timeout(200);continue
            nb=pg.locator('#nextBtn, #rebuyBtn, #restartBtn')
            if await nb.count(): await nb.first.click()
            elif not await pg.locator('#bCall').is_disabled():
                r=random.random()
                if r<.3 and not await pg.locator('#bRaise').is_disabled():
                    await pg.click('#bRaise');await pg.wait_for_timeout(80)
                    if raised==0: await pg.screenshot(path='/tmp/ux_raise.png')
                    sizes=await pg.locator('.size').count()
                    if sizes: await pg.locator('.size').nth(random.randrange(sizes)).click()
                    await pg.click('#bConfirm');await pg.wait_for_timeout(60)
                    if await pg.locator('#bConfirm.armed').count(): await pg.click('#bConfirm')
                    raised+=1
                elif r<.45: await pg.click('#bFold')
                else: await pg.click('#bCall')
            await pg.wait_for_timeout(220)
        # seat info
        await pg.locator('.pseat').first.click();await pg.wait_for_timeout(150)
        await pg.screenshot(path='/tmp/ux_seat.png')
        await pg.click('#pClose')
        await pg.click('#histBtn');await pg.wait_for_timeout(200)
        await pg.evaluate("document.querySelector('.hitem')&&(document.querySelector('.hitem').open=true)")
        el=await pg.query_selector('#histPanel');await el.screenshot(path='/tmp/ux_hist.png')
        print('paused',paused,'raised',raised,'hands',await pg.evaluate("G.hand"),'decs',await pg.evaluate("G.stats.dec"),'lv',await pg.evaluate("JSON.stringify(G.stats.lv)"))
        print('scrollW',await pg.evaluate('document.documentElement.scrollWidth'))
        print('ERR',errs[:6]);await b.close()
asyncio.run(main())

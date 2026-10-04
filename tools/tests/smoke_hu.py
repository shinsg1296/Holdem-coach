import asyncio,sys
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':400,'height':860});await pg.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        await pg.goto(URL); await pg.wait_for_timeout(800)
        await pg.click('.mode[data-m="hu"]'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/hu_map.png')
        await pg.click('.hucard[data-i="0"]'); await pg.wait_for_timeout(200)
        await pg.click('#huGo'); await pg.wait_for_timeout(500)
        for i in range(150):
            if await pg.locator('#huNext').count() or await pg.locator('#huRetry').count(): break
            if await pg.locator('#nextBtn').count(): await pg.click('#nextBtn')
            elif not await pg.locator('#bCall').is_disabled(): await pg.click('#bCall')
            await pg.wait_for_timeout(300)
        await pg.evaluate("document.querySelector('.notes')&&(document.querySelector('.notes').open=true)")
        await pg.screenshot(path='/tmp/hu_play.png',full_page=True)
        print('result',await pg.locator('#resultBox').inner_text())
        await pg.click('.mode[data-m="live"]'); await pg.wait_for_timeout(1200)
        print('live seats',await pg.locator('.seat').count(),'banner hidden',await pg.locator('#huBanner').is_hidden())
        await pg.click('.mode[data-m="hu"]'); await pg.wait_for_timeout(300)
        print('hu stars',await pg.locator('.hucard .sstars').all_inner_texts())
        print('ERRORS',errs)
        await b.close()
asyncio.run(main())

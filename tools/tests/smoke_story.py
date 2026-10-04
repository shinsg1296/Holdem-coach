import asyncio
import sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':400,'height':860});await pg.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        await pg.goto(sys.argv[1])
        await pg.wait_for_timeout(800)
        await pg.click('.mode[data-m="story"]'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/s_map.png')
        # play stages 1..9 choosing best
        for sid in range(1,10):
            await pg.click(f'.scard[data-id="{sid}"]') if sid==1 else None
            best=await pg.evaluate("SV.stage.nodes[SV.node].best")
            await pg.click(f'.sopt[data-o="{best}"]'); await pg.wait_for_timeout(150)
            await pg.click('#sGo'); await pg.wait_for_timeout(150)
        # boss: raise then allin
        await pg.click('.sopt[data-o="raise"]'); await pg.wait_for_timeout(150)
        await pg.screenshot(path='/tmp/s_boss1.png',full_page=True)
        await pg.click('#sNext'); await pg.wait_for_timeout(150)
        await pg.click('.sopt[data-o="allin"]'); await pg.wait_for_timeout(150)
        await pg.screenshot(path='/tmp/s_boss2.png',full_page=True)
        print('progress',await pg.evaluate("localStorage.getItem('holdem-story-v1')"))
        await pg.click('#sBack'); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/s_map2.png')
        print('ERRORS',errs)
        await b.close()
asyncio.run(main())

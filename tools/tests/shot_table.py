import asyncio,sys
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for n,w in [('5',400),('8',400),('2',400),('6',900)]:
            pg=await b.new_page(viewport={'width':w,'height':900});await pg.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
            errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
            await pg.goto(URL);await pg.evaluate(f"localStorage.clear();localStorage.setItem('holdem-np','{n}')");await pg.goto(URL);await pg.wait_for_timeout(500)
            await pg.add_style_tag(content='[hidden]{display:none!important}')
            for i in range(25):
                if await pg.locator('#nextBtn').count(): await pg.click('#nextBtn')
                elif not await pg.locator('#bCall').is_disabled(): break
                await pg.wait_for_timeout(300)
            await pg.wait_for_timeout(300)
            sw=await pg.evaluate('document.documentElement.scrollWidth')
            el=await pg.query_selector('.tablewrap')
            await el.screenshot(path=f'/tmp/tbl_{n}_{w}.png')
            print(n,w,'scrollWidth',sw,'errs',errs)
            await pg.close()
        await b.close()
asyncio.run(main())

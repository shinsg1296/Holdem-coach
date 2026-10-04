import asyncio,sys
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':400,'height':860})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.goto(URL);await pg.wait_for_timeout(900)
        await pg.add_style_tag(content='[hidden]{display:none!important}')
        await pg.screenshot(path='/tmp/x_welcome.png')
        await pg.click('#w2');await pg.wait_for_timeout(200);await pg.click('#tStart')
        while await pg.locator('.sopt').count():
            a=await pg.evaluate("LV.items[LV.i].answer");await pg.click(f'.sopt[data-j="{a}"]');await pg.click('#tNext')
        print('placement:',await pg.locator('.result h2').inner_text(),await pg.evaluate("localStorage.getItem('holdem-story-v1')"))
        await pg.click('#tList');await pg.wait_for_timeout(100)
        q1=None
        await pg.click('#dailyBtn');await pg.click('#tStart')
        q1=await pg.evaluate("LV.items.map(i=>i.q+i.answer+i.show.length).join('|')")
        while await pg.locator('.sopt').count():
            a=await pg.evaluate("LV.items[LV.i].answer");await pg.click(f'.sopt[data-j="{a}"]');await pg.click('#tNext')
        print('daily:',(await pg.locator('.result').inner_text()).replace('\n',' / ')[:120])
        await pg.click('#sRetry');await pg.click('#tStart')
        q2=await pg.evaluate("LV.items.map(i=>i.q+i.answer+i.show.length).join('|')")
        print('same daily questions on retry:',q1==q2)
        await pg.click('#sBack');await pg.wait_for_timeout(100)
        await pg.screenshot(path='/tmp/x_map.png')
        await pg.click('#optBtn');await pg.select_option('#themeSel','blue');await pg.click('.mode[data-m="live"]');await pg.wait_for_timeout(1500)
        for i in range(20):
            if await pg.locator('#nextBtn').count(): await pg.click('#nextBtn')
            elif not await pg.locator('#bCall').is_disabled(): await pg.click('#bCall')
            await pg.wait_for_timeout(250)
        print('rating',await pg.evaluate("localStorage.getItem('holdem-rating-v1')"))
        el=await pg.query_selector('.tablewrap');await el.screenshot(path='/tmp/x_blue.png')
        print('ERR',errs);await b.close()
asyncio.run(main())

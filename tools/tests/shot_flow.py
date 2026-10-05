"""Screenshots along one live hand and the secondary screens, at phone size, for UI review.
usage: python3 tools/tests/shot_flow.py URL OUTDIR [WIDTH HEIGHT]"""
import asyncio,sys,os
from playwright.async_api import async_playwright
URL=sys.argv[1];OUT=sys.argv[2];os.makedirs(OUT,exist_ok=True)
W=int(sys.argv[3]) if len(sys.argv)>3 else 360;H=int(sys.argv[4]) if len(sys.argv)>4 else 740
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True)
        await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
        await ctx.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.add_style_tag(content='[hidden]{display:none!important}')
        async def shot(n,full=False): await pg.screenshot(path=os.path.join(OUT,n+('_full' if full else '')+'.png'),full_page=full)
        async def my_turn():
            for _ in range(200):
                if not await pg.locator('#bCall').is_disabled(): return True
                if await pg.locator('#cta button').count(): return False
                await pg.wait_for_timeout(150)
            return False
        # one decision, then the feedback it produces
        if await my_turn():
            await pg.click('#bCall');await pg.wait_for_timeout(700);await shot('a1_after_action');await shot('a1_after_action',True)
        # play on until the hand is over
        for _ in range(12):
            if await pg.locator('#cta button').count(): break
            if await my_turn(): await pg.click('#bFold');await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(1500);await shot('a2_hand_over');await shot('a2_hand_over',True)
        print('result buttons',await pg.evaluate("[...document.querySelectorAll('#cta button')].map(b=>[b.id,b.textContent.trim(),Math.round(b.getBoundingClientRect().top),innerHeight])"))
        if await pg.locator('#histBtn').count():
            await pg.click('#histBtn');await pg.wait_for_timeout(400);await shot('a3_history',True)
        await pg.click('#optBtn');await pg.wait_for_timeout(200);await shot('a4_options')
        if await pg.locator('#setBtn').count():
            await pg.click('#setBtn');await pg.wait_for_timeout(200);await shot('a5_settings',True)
        await pg.click('.mode[data-m="story"]');await pg.wait_for_timeout(400)
        await pg.click('.scard[data-t="t1"]');await pg.wait_for_timeout(500);await shot('b1_lesson');await shot('b1_lesson',True)
        await pg.click('.mode[data-m="story"]');await pg.wait_for_timeout(300)
        if await pg.locator('.scard[data-id="1"]').count():
            await pg.click('.scard[data-id="1"]');await pg.wait_for_timeout(600);await shot('b2_stage');await shot('b2_stage',True)
        await pg.click('.mode[data-m="hu"]');await pg.wait_for_timeout(400)
        if await pg.locator('.hucard').count():
            await pg.locator('.hucard').first.click();await pg.wait_for_timeout(600);await shot('c1_hu_intro',True)
        print('ERR',errs[:5]);await b.close()
asyncio.run(main())

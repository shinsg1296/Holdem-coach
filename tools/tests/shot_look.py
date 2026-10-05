"""Screenshots for judging the look: web fonts are allowed to load and the phone is emulated as a touch device.
usage: python3 tools/tests/shot_look.py URL OUTDIR [WIDTH HEIGHT]"""
import asyncio,sys,os
from playwright.async_api import async_playwright
URL=sys.argv[1];OUT=sys.argv[2];os.makedirs(OUT,exist_ok=True)
W=int(sys.argv[3]) if len(sys.argv)>3 else 360;H=int(sys.argv[4]) if len(sys.argv)>4 else 740
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True)
        await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1');localStorage.setItem('holdem-fbcfg','{\"local\":true}')}catch(e){}")
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.add_style_tag(content='[hidden]{display:none!important}');await pg.wait_for_timeout(1500)
        shot=lambda n:pg.screenshot(path=os.path.join(OUT,n+'.png'))
        async def my_turn():
            for _ in range(200):
                if not await pg.locator('#bCall').is_disabled(): return True
                if await pg.locator('#cta button').count(): return False
                await pg.wait_for_timeout(150)
            return False
        if await my_turn():
            await pg.wait_for_timeout(600);await shot('1_turn')
            if not await pg.locator('#bRaise').is_disabled():
                await pg.click('#bRaise');await pg.wait_for_timeout(300);await shot('2_raise');await pg.click('#bCancel')
            await pg.click('#bCall');await pg.wait_for_timeout(900)
        for _ in range(14):
            if await pg.locator('#cta button').count(): break
            if await my_turn(): await pg.click('#bCall');await pg.wait_for_timeout(700)
        await pg.wait_for_timeout(1600);await shot('3_hand_over')
        await pg.evaluate("window.scrollTo(0,420)");await pg.wait_for_timeout(300);await shot('4_feedback');await pg.evaluate("window.scrollTo(0,0)")
        await pg.click('.mode[data-m="story"]');await pg.wait_for_timeout(600);await shot('5_story')
        await pg.click('.mode[data-m="hu"]');await pg.wait_for_timeout(600);await shot('6_headsup')
        await pg.click('.mode[data-m="mp"]');await pg.wait_for_timeout(600);await shot('7_friends')
        print('ERR',errs[:5]);await b.close()
asyncio.run(main())

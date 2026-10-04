"""Screenshots of every main screen for UI review.
usage: python3 tools/tests/shot_all.py URL OUTDIR [WIDTH HEIGHT] [full]  (full = whole page instead of what the phone shows)"""
import asyncio,sys,os
from playwright.async_api import async_playwright
URL=sys.argv[1];OUT=sys.argv[2];os.makedirs(OUT,exist_ok=True)
W=int(sys.argv[3]) if len(sys.argv)>3 else 400;H=int(sys.argv[4]) if len(sys.argv)>4 else 860;FULL='full' in sys.argv
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':W,'height':H},device_scale_factor=2)
        await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1');localStorage.setItem('holdem-fbcfg','{\"local\":true}')}catch(e){}")
        await ctx.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.add_style_tag(content='[hidden]{display:none!important}');await pg.wait_for_timeout(2500)
        shot=lambda n:pg.screenshot(path=os.path.join(OUT,n+'.png'),full_page=FULL)
        await shot('01_live')
        print('modes',await pg.evaluate("[...document.querySelectorAll('.mode')].map(b=>b.dataset.m+':'+b.textContent.trim())"))
        print('buttons',await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>(b.id||'')+':'+b.textContent.trim().slice(0,14)).slice(0,40)"))
        # open raise panel if hero to act
        for sel in ['#bRaise:not([disabled])','#raiseBtn','button:has-text(\"레이즈\")','button:has-text(\"벳\")']:
            if await pg.locator(sel).count():
                try: await pg.locator(sel).first.click(timeout=1500);await pg.wait_for_timeout(400);await shot('02_live_raise');break
                except Exception: pass
        for m in await pg.evaluate("[...document.querySelectorAll('.mode')].map(b=>b.dataset.m)"):
            try:
                await pg.click(f'.mode[data-m="{m}"]',timeout=2000);await pg.wait_for_timeout(1200);await shot('10_mode_'+m)
            except Exception as e: print('skip',m,str(e)[:80])
        print('scroll',await pg.evaluate('[document.documentElement.scrollWidth,document.documentElement.scrollHeight,innerHeight]'));print('ERR',errs[:5]);await b.close()
asyncio.run(main())

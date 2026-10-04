"""Screenshots of the multiplayer table (local transport): the player to act, the raise panel, and a waiting player.
usage: python3 tools/tests/shot_mp.py URL OUTDIR [WIDTH HEIGHT]"""
import asyncio,sys,os
from playwright.async_api import async_playwright
URL=sys.argv[1];OUT=sys.argv[2];os.makedirs(OUT,exist_ok=True)
W=int(sys.argv[3]) if len(sys.argv)>3 else 360;H=int(sys.argv[4]) if len(sys.argv)>4 else 740
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':W,'height':H},device_scale_factor=2)
        await ctx.add_init_script("try{localStorage.setItem('holdem-welcomed','1');localStorage.setItem('holdem-fbcfg','{\"local\":true}')}catch(e){}")
        await ctx.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        errs=[];pages=[]
        for i in range(3):
            pg=await ctx.new_page();pg.on('pageerror',lambda e,i=i:errs.append(f'{i}:{e}'))
            await pg.goto(URL);await pg.wait_for_timeout(400)
            if i==0: await pg.evaluate("localStorage.removeItem('holdem-mp-store')")
            await pg.add_style_tag(content='[hidden]{display:none!important}')
            await pg.click('.mode[data-m="mp"]');await pg.fill('#mpName',['형','민수','지훈'][i]);pages.append(pg)
        await pages[0].click('#mpNew');await pages[0].wait_for_timeout(400)
        code=await pages[0].locator('.mpcode').inner_text()
        for pg in pages[1:]:
            await pg.fill('#mpCodeIn',code);await pg.click('#mpJoinBtn');await pg.wait_for_timeout(300)
        await pages[0].wait_for_timeout(800);await pages[0].click('#mpStart');await pages[0].wait_for_timeout(4000)
        for k,pg in enumerate(pages):
            if await pg.locator('#mpRopen').count():
                await pg.bring_to_front();await pg.screenshot(path=os.path.join(OUT,'mp_turn.png'))
                await pg.click('#mpRopen');await pg.wait_for_timeout(200);await pg.screenshot(path=os.path.join(OUT,'mp_raise.png'))
                other=pages[(k+1)%3];await other.bring_to_front();await other.wait_for_timeout(1200);await other.screenshot(path=os.path.join(OUT,'mp_wait.png'))
                print('fits',await pg.evaluate('[document.documentElement.scrollWidth,document.documentElement.scrollHeight,innerHeight]'));break
        print('ERR',errs[:5]);await b.close()
asyncio.run(main())

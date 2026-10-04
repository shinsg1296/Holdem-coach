import asyncio,sys
from playwright.async_api import async_playwright
URL=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':400,'height':860});await pg.add_init_script("try{localStorage.setItem('holdem-welcomed','1')}catch(e){}")
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
        await pg.goto(URL);await pg.wait_for_timeout(600)
        r=await pg.evaluate("""()=>{const out={};for(let t=0;t<10;t++){let ok=0;for(let i=0;i<200;i++){const c=gen5(t);if(c&&cat10(c)===t&&new Set(c).size===5)ok++}out['g'+t]=ok}
          let bad=0;for(let i=0;i<300;i++){const q=GEN.name5();if(!q.options[q.answer])bad++;const w=GEN.winner();if(w.answer<0||w.answer>2)bad++;const b=GEN.best7();if(b.answer<0)bad++;const r=GEN.rank2();if(r.answer<0)bad++}
          out.bad=bad;let split=0,same=0;for(let i=0;i<200;i++){const w=GEN.winner();if(w.answer===2)split++;if(/^둘 다/.test(w.why))same++}out.split=split;out.same=same;return out}""")
        print(r)
        await pg.click('.mode[data-m="story"]');await pg.wait_for_timeout(200)
        for t in ['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10']:
            await pg.click(f'.scard[data-t="{t}"]') if t=='t1' else None
            await pg.click('#tStart');await pg.wait_for_timeout(100)
            if t=='t2': await pg.screenshot(path='/tmp/tut_q.png',full_page=True)
            while await pg.locator('.sopt').count():
                ans=await pg.evaluate("LV.items[LV.i].answer")
                await pg.click(f'.sopt[data-j="{ans}"]');await pg.wait_for_timeout(30)
                if t=='t4' and await pg.evaluate("LV.i")==0: await pg.screenshot(path='/tmp/tut_best7.png',full_page=True)
                await pg.click('#tNext');await pg.wait_for_timeout(30)
            if t!='t10': await pg.click('#sGo');await pg.wait_for_timeout(50)
        print('progress',await pg.evaluate("localStorage.getItem('holdem-story-v1')"))
        await pg.click('#sBack');await pg.wait_for_timeout(100)
        await pg.screenshot(path='/tmp/tut_map.png')
        print('ERR',errs);await b.close()
asyncio.run(main())

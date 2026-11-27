from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':760});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.evaluate("""()=>{const d=getDay('2026-11-15');Object.assign(d,{total:'300',start:'1',end:'150',returns:[{id:'r',no:5,qty:1,reason:'拒收',at:1}],fReturns:[{id:'f',qty:2,reason:'拒收',at:1}],
      ded:[{id:'a',amount:45.5,note:'包裹損壞賠償',confirmed:true,at:1},{id:'b',amount:20,note:'可能要賠',confirmed:false,at:2}]});touch('days',d);
      S.ui.sFrom='2026-11-09';S.ui.sTo='2026-11-15';persist();go('week')}""")
    print(pg.evaluate("settleText()"));print(pg.inner_text('.card:has(h3:text("每人合計"))').replace('\n',' '))
    pg.evaluate("S.ui.wv='pay';render()");print(pg.inner_text('.wk').replace('\n',' '))
    pg.evaluate("go('stat');setUI('period','all')");print(pg.inner_text('.card:has(h3:text("收入"))').replace('\n',' '))
    pg.evaluate("go('day');setDate('2026-11-15')");pg.screenshot(path='/tmp/pp_d2.png',full_page=True);print(errs);b.close()

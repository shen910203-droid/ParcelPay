from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    inp=pg.locator('.stp:has-text("到倉庫") input')
    inp.focus()
    # simulate wheel: change events fire while still focused
    inp.evaluate("e=>{e.value='06:00';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
    still=pg.evaluate("document.activeElement&&document.activeElement.type==='time'")
    saved=pg.evaluate("getDay(today()).t.arrive||''")
    inp.evaluate("e=>{e.value='06:15';e.dispatchEvent(new Event('change',{bubbles:true}))}")
    print('during picking: still focused',still,'saved yet:',repr(saved))
    pg.evaluate("document.activeElement.blur()")
    print('after done: saved',pg.evaluate("getDay(today()).t.arrive"),'✓ count',pg.locator('.stp.ok').count())
    # date picker
    d=pg.locator('.dpick input');d.focus();d.evaluate("e=>{e.value='2026-11-20';e.dispatchEvent(new Event('change',{bubbles:true}))}")
    print('date during picking curDate',pg.evaluate('curDate'));pg.evaluate("document.activeElement.blur()");print('after blur',pg.evaluate('curDate'))
    print(errs);b.close()

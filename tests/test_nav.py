from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.evaluate("go('fuel')");pg.locator('input[inputmode=decimal]').first.focus()
    print('typing while focused:',pg.evaluate("document.body.classList.contains('typing')"))
    # simulate Safari: focused input removed by re-render without focusout
    pg.evaluate("document.body.classList.add('typing');go('day')")
    pg.wait_for_timeout(100);print('after re-render typing:',pg.evaluate("document.body.classList.contains('typing')"),'nav visible:',pg.locator('nav').is_visible())
    print('sheet hidden visibility:',pg.evaluate("getComputedStyle(document.getElementById('sheet2')).visibility"),'shadow:',pg.evaluate("getComputedStyle(document.getElementById('sheet2')).boxShadow"))
    print(errs);b.close()

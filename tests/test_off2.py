from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    for kind,btn in [('me','🏖 我休假'),('all','😴 全員休息')]:
        pg.evaluate("setDate(addDays(today(),%d))"%(-1 if kind=='me' else -2)); pg.tap('text='+btn)
        if kind=='me': pg.locator('.card:has(h3:text("同區統計")) input').nth(0).fill('280')
        pg.tap('text=✅ 當日結算完成'); print(kind,'locked',pg.evaluate("getDay(curDate).locked"),'lockbar',pg.locator('.lockbar').count())
        pg.tap('text=解鎖編輯'); print(kind,'unlocked',not pg.evaluate("getDay(curDate).locked"))
    print(errs);b.close()

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);calls=[]
    ctx.route('https://script.google.com/**',lambda r:(calls.append(1),r.fulfill(status=200,content_type='application/json',body='{"ok":true,"items":[]}')))
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.evaluate("setLocal('url','https://script.google.com/macros/s/X/exec');setLocal('token','t');go('set')")
    pg.tap('text=自動同步'); print('auto:',pg.evaluate('autoOn()'))
    n0=len(calls); pg.evaluate("setDate(today());go('day');const d=getDay(today());Object.assign(d,{start:'100',end:'105',total:'6'});touch('days',d)"); pg.wait_for_timeout(2500)
    print('calls while off:',len(calls)-n0,'badge:',pg.inner_text('#badge'))
    pg.evaluate("go('set')"); pg.tap('button:has-text("立即同步")'); pg.wait_for_timeout(1500); print('after manual:',len(calls)-n0,'pending',pg.evaluate('S.pending.length'),'badge:',pg.inner_text('#badge'))
    pg.tap('text=自動同步'); n1=len(calls); pg.evaluate("const d=getDay(today());d.note='x';touch('days',d)"); pg.wait_for_timeout(2500); print('auto on calls:',len(calls)-n1)
    pg.evaluate("openRun()"); pg.locator('.pr:has(b:text-is("103")) .more').tap(); pg.tap('text=跳號（沒這號）')
    c=pg.evaluate("JSON.stringify((({assigned,delivered})=>({assigned,delivered}))(calc(getDay(today()))))")
    print('after skip 103:',pg.evaluate("pkRows(getDay(today())).map(r=>r.key).join(' ')"),c)
    pg.evaluate("pkDo('104','plus')");pg.locator('.pr:has(b:text-is("104-1")) .more').tap();print('skip btn on multi row:',pg.locator('text=跳號（沒這號）').count())
    print(errs);b.close()

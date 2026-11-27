from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:d.accept())
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    # flow today
    pg.tap('text=🚗 出門'); pg.tap('text=📦 到倉庫，開始點貨')
    print('run?',pg.evaluate('S.ui.run'),'head',pg.inner_text('.runtop'))
    ins=pg.locator('.card:has(h3:text("編號範圍")) input'); ins.nth(0).fill('130'); ins.nth(1).fill('269'); pg.locator('.card:has(h3:text("全帳號核對")) input').nth(2).fill('300')
    q=pg.locator('#qno')
    for n in ['151','169','172','50']: q.fill(n); pg.tap('.qbtn >> text=缺件')
    pg.tap('text=▶ 點完了，開始送貨')
    print('stage',pg.evaluate('nextStep(getDay(today()))'),pg.inner_text('.runtop'))
    for n,k in [('144',1),('188',1),('199',1),('200',2),('269',5)]:
        q.fill(n)
        for _ in range(k): pg.tap('.qbtn >> text=多件 +1')
    q.fill('166'); pg.tap('.qbtn >> text=退件'); pg.tap('#qreason >> text=地址錯誤')
    q.fill('2'); q.type('3')  # draft typed, not saved
    # simulate app killed & reopened
    pg.reload(); pg.wait_for_timeout(300)
    print('after reload run?',pg.evaluate('S.ui.run'),'draft kept:',pg.input_value('#qno'),'delivered',pg.evaluate("calc(getDay(today())).delivered"))
    print('first rows:',[t.replace('\n',' ') for t in pg.locator('#lists .ev').all_inner_texts()[:3]])
    pg.screenshot(path='/tmp/pp_v4_run.png',full_page=True)
    pg.tap('text=✓ 送完')
    print('back home run?',pg.evaluate('S.ui.run'),'stage',pg.evaluate('nextStep(getDay(today()))'))
    pg.fill('#fq','5'); pg.tap('.frow >> text=無人簽收')
    pg.tap('text=🏠 到家（下班打卡）')
    c=json.loads(pg.evaluate("JSON.stringify(calc(getDay(today())))"))
    print('final me',c['delivered'],'F',c['fDelivered'],'commute',c['commute'])
    pg.screenshot(path='/tmp/pp_v4_home.png',full_page=True)
    # meOff day yesterday
    pg.evaluate("setDate(addDays(today(),-1))"); pg.tap('text=🏖 我休假')
    g=pg.locator('.card:has(h3:text("同區統計")) input'); g.nth(0).fill('280'); g.nth(1).fill('2')
    pg.fill('#fq','3'); pg.tap('.frow >> text=拒收')
    c=json.loads(pg.evaluate("JSON.stringify(calc(getDay(addDays(today(),-1))))")); print('meOff F',c['fDelivered'],'(280-2-3=275)')
    pg.tap('text=今天有支援人員'); pg.locator('.card:has(h3:text("同區統計")) .g2 input').nth(2).fill('150')  # v5.9：Frankie 說他送達 移到「Frankie 說他」那一列
    s=pg.locator('.card:has(h3:text("同區統計")) .g3 input'); s.nth(1).fill('1')
    c=json.loads(pg.evaluate("JSON.stringify(calc(getDay(addDays(today(),-1))))")); print('meOff+sup F',c['fDelivered'],'S',c['sDelivered'],'(280-2-150-3-1=124)')
    pg.screenshot(path='/tmp/pp_v4_off.png',full_page=True)
    pg.evaluate("setDate(addDays(today(),-2))"); pg.tap('text=😴 全員休息')
    pg.evaluate("setSettle('this');go('week')"); print(pg.evaluate("settleText()"))
    pg.screenshot(path='/tmp/pp_v4_settle.png',full_page=True)
    # backfill past date via edit button
    pg.evaluate("go('day');setDate(addDays(today(),-3))"); pg.tap('text=✏️ 補登 / 修改件數'); print('backfill head',pg.inner_text('.runtop'),'has range inputs',pg.locator('.card:has(h3:text("編號範圍"))').count())
    for w in (320,390):
        pg.set_viewport_size({'width':w,'height':700})
        for fn in ["exitRun();setDate(today())","openRun()","exitRun();setDate(addDays(today(),-1))","go('week')"]:
            pg.evaluate(fn); pg.wait_for_timeout(80)
            ov=pg.evaluate("""()=>{const o=[];document.querySelectorAll('body *').forEach(e=>{if(e.closest('.tbl'))return;const r=e.getBoundingClientRect();if(r.width&&r.right>innerWidth+1)o.push(e.tagName+'.'+e.className)});return o.slice(0,4)}""")
            if ov: print(w,fn,'OVERFLOW',ov)
    print('errors',errs); b.close()

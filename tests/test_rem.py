from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    log=[];ans={'confirm':[False,True],'prompt':['182.5']}
    def dlg(d):
        log.append((d.type,d.message.replace('\n',' ')))
        if d.type=='confirm':d.accept() if ans['confirm'].pop(0) else d.dismiss()
        elif d.type=='prompt':d.accept(ans['prompt'].pop(0))
        else:d.accept()
    pg.on('dialog',dlg)
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.click('text=🚗 出門');print('after cancel leave:',repr(pg.evaluate("getDay(today()).t.leave")))
    pg.click('text=🚗 出門');print('after ok leave:',pg.evaluate("getDay(today()).t.leave"))
    pg.evaluate("const d=getDay(today());d.t={...d.t,arrive:'06:00',start:'07:00',end:'14:00'};touch('days',d);exitRun();render()")
    pg.click('text=🏠 到家（下班打卡）');print('kmB:',pg.evaluate("getDay(today()).kmB"),'km calc:',pg.evaluate("calc(getDay(today())).km"))
    for l in log:print(' ',l)
    # evening
    print(pg.evaluate("""()=>{const d=newDay('2026-12-01');Object.assign(d,{mode:'evening',kmBe:'30',kmB:'150'});return calc(d).km}"""),'期望 180')
    print(errs);b.close()

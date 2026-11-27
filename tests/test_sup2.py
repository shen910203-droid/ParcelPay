from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    print(pg.evaluate("""()=>{const d=newDay('2026-11-25');Object.assign(d,{total:'373',start:'1',end:'100',multi:[{id:'m',no:5,qty:10,at:1}],
      returns:[1,2,3].map(n=>({id:'r'+n,no:n,qty:1,reason:'x',at:n})),fReturns:[{id:'f',qty:5,reason:'x',at:1}],sup:{on:true,name:'Bruce',fDel:'130',sRet:''}});
      const c=calc(d);return [APP_VERSION,c.delivered,c.fDelivered,c.sDelivered,c.delivered+c.fDelivered+c.sDelivered+c.myRet+c.fRet]}"""),'期望 106 / 130 / 129 / 373',errs);b.close()

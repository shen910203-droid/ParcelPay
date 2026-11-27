from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    r=pg.evaluate("""()=>{const d=newDay('2026-11-24');Object.assign(d,{acStart:'1',acEnd:'271',total:'294',start:'130',end:'269',
      skip:[{id:'a',no:245,at:1},{id:'b',no:30,at:2}],multi:[{id:'m',no:200,qty:3,at:3},{id:'n',no:20,qty:2,at:4}],missing:[{id:'x',no:151,qty:1,at:5}]});
      S.days[d.date]=d;curDate=d.date;openRun();const c=calc(d);return [c.numbers,c.extra,c.delivered,c.fDelivered,document.getElementById('acres').innerText.replace(/\\n/g,' ')]}""")
    print(r,'期望: numbers 139, extra 2, delivered 140, F=294-141-0=153; 核對: 271-2=269號, 多件應有 25, 已標 3, 還差 22')
    print(errs);b.close()

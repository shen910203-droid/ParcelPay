from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    for w in (320,390):
        pg=b.new_page(viewport={'width':w,'height':800},is_mobile=True,has_touch=True);pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
        pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
        pg.evaluate("setDate(addDays(today(),1))");pg.tap('text=✏️ 補登 / 修改件數')
        ac=pg.locator('.card:has(h3:text("全帳號核對")) input');ac.nth(0).fill('1');ac.nth(1).fill('271');ac.nth(2).fill('296')
        print(w,'start:',pg.inner_text('#acres').replace('\n',' '))
        q=pg.locator('#qno')
        marks=[(20,2),(55,3),(144,2),(188,2),(200,3),(269,6),(270,2)]
        for n,k in marks:
            q.fill(str(n))
            for _ in range(k-1): pg.tap('.qbtn >> text=多件 +1')
        print(w,'after marks:',pg.inner_text('#acres').replace('\n',' '))
        # next day: set my range
        r=pg.locator('.card:has(h3:text("編號範圍")) input');r.nth(0).fill('130');r.nth(1).fill('269')
        c=pg.evaluate("JSON.stringify((({numbers,extra,delivered,fDelivered,warn})=>({numbers,extra,delivered,fDelivered,warn}))(calc(getDay(curDate))))");print(w,c)
        pg.evaluate("toggleSec('multi');toggleSec('others')")
        print(w,'sections:',[t.split('\n')[0:2] for t in pg.locator('.sech2').all_inner_texts()])
        pg.screenshot(path=f'/tmp/pp_pre_{w}.png',full_page=True)
        ov=pg.evaluate("""()=>{const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&r.right>innerWidth+1)o.push(e.tagName+'.'+e.className)});
          document.querySelectorAll('.card,.evlist,.sec2,.g3,.acres').forEach(c=>{const ch=[...c.children].filter(x=>x.offsetParent);for(let i=1;i<ch.length;i++){const a=ch[i-1].getBoundingClientRect(),b=ch[i].getBoundingClientRect();if(b.top<a.bottom-1&&b.left<a.right-1&&a.left<b.right-1)o.push('OVERLAP '+c.className)}});return o.slice(0,5)}""");print(w,'ov',ov)
    print(errs);b.close()

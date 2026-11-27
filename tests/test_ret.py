from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    def run(o):return pg.evaluate("""o=>{const d=newDay('2026-11-20');Object.assign(d,o);const c=calc(d);return [c.numbers,c.extra,c.delivered,c.fDelivered]}""",o)
    R=lambda no,q=1:{'id':str(no)+str(q),'no':no,'qty':q,'reason':'x'}
    print('1-159, 150 退兩筆:',run({'start':'1','end':'159','total':'300','returns':[R(150),{**R(150),'id':'z'}]}),'期望 159號 +1 → 158')
    print('150 一筆退×2:',run({'start':'1','end':'159','returns':[R(150,2)]}),'期望 158')
    print('150 共3件(多件)、退2:',run({'start':'1','end':'159','multi':[{'id':'m','no':150,'qty':3}],'returns':[R(150,2)]}),'期望 159+2-2=159')
    print('150 多件2、退1:',run({'start':'1','end':'159','multi':[{'id':'m','no':150,'qty':2}],'returns':[R(150)]}),'期望 160-1=159')
    print('原範例:',run({'start':'130','end':'269','total':'300','missing':[R(151),R(169),R(172),R(50)],'multi':[{'id':'a','no':n,'qty':q} for n,q in [(144,2),(188,2),(199,2),(200,3),(269,6)]],'returns':[R(166)]}),'期望 146 / F144')
    print('缺件150×2 未標多件:',run({'start':'1','end':'159','missing':[R(150,2)]}),'期望 158')
    print(errs);b.close()

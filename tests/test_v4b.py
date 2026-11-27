from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    pg=b.new_page(viewport={'width':320,'height':700},is_mobile=True,has_touch=True); pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:d.accept())
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.evaluate("""()=>{const t=today(),mk=(dt,o)=>{const d=getDay(dt);Object.assign(d,o);touch('days',d)};
      mk(t,{total:'300',start:'130',end:'269',t:{leave:'05:30',arrive:'06:00',start:'07:15',end:'',home:''},
        missing:[{id:'a',no:151,qty:1,at:1},{id:'b',no:50,qty:1,at:2}],multi:[{id:'c',no:200,qty:3,at:3}],returns:[{id:'d',no:166,qty:1,reason:'找不到地址',at:4}]});
      mk(addDays(t,-7),{offType:'me',total:'280',offMiss:'2',fReturns:[{id:'e',qty:3,reason:'拒收',at:5}],sup:{on:true,name:'Tom',fDel:'150',sRet:'1'}});
      mk(addDays(t,-6),{offType:'all'});mk(addDays(t,-5),{total:'296',start:'1',end:'150',locked:true});render()}""")
    for w in (320,390):
        pg.set_viewport_size({'width':w,'height':700})
        for name,fn in [('home',"exitRun();setDate(today())"),('run',"openRun()"),('meoff',"exitRun();setDate(addDays(today(),-7))"),('allof',"setDate(addDays(today(),-6))"),('settle',"setSettle('last');go('week')")]:
            pg.evaluate(fn); pg.wait_for_timeout(80)
            ov=pg.evaluate("""()=>{const o=[];document.querySelectorAll('body *').forEach(e=>{if(e.closest('.tbl'))return;const r=e.getBoundingClientRect();if(r.width&&r.right>innerWidth+1)o.push(e.tagName+'.'+e.className)});return o.slice(0,4)}""")
            print(w,name,'OVERFLOW' if ov else 'ok',ov)
            pg.screenshot(path=f'/tmp/pp_b_{w}_{name}.png',full_page=True)
    print(pg.evaluate("settleText()"))
    print('errors',errs); b.close()

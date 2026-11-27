from playwright.sync_api import sync_playwright
import sys
SEED="""()=>{const t=today(),mk=(dt,o)=>{const d=getDay(dt);Object.assign(d,o);touch('days',d)};const n=Date.now();
 mk(t,{total:'300',start:'130',end:'269',kmB:'182',acStart:'1',acEnd:'271',t:{leave:'05:30',arrive:'06:00',start:'07:15',end:'14:45',home:'15:20'},
  missing:[{id:'a',no:151,qty:1,at:n-9e6},{id:'b2',no:50,qty:1,at:n-7e6}],multi:[{id:'c',no:200,qty:3,at:n-5e6},{id:'c2',no:20,qty:2,at:n-4e6}],skip:[{id:'s',no:245,at:n-3e6}],
  returns:[{id:'d',no:166,qty:1,reason:'找不到地址',at:n-3e6}],fReturns:[{id:'f',qty:5,reason:'無人簽收',at:n-1e6}],ded:[{id:'x',amount:45.5,note:'包裹損壞賠償',confirmed:true,at:n},{id:'y',amount:20,note:'可能要賠',confirmed:false,at:n}]});
 mk(addDays(t,-1),{offType:'me',total:'280',offMiss:'2',sup:{on:true,name:'Tom',fDel:'150',sRet:'1'}});
 mk(addDays(t,-2),{offType:'all'});mk(addDays(t,-7),{total:'296',start:'1',end:'150',locked:true});
 touch('fuel',{id:'f1',date:addDays(t,-3),amount:41.8,liters:20.3,tripA:177,full:true});touch('fuel',{id:'f2',date:addDays(t,-1),amount:22,liters:10,tripA:'',full:false,note:'只加一半'});
 S.ui.sec={returns:true,missing:true,multi:true,skip:true,others:true,fReturns:true};render()}"""
WRAP="""()=>{const out=[];const w=document.createTreeWalker(document.getElementById('view'),NodeFilter.SHOW_TEXT);let nd;
 while(nd=w.nextNode()){const t=nd.textContent.trim();if(t.length<2)continue;const el=nd.parentElement;if(!el.offsetParent)continue;if(el.closest('textarea,input'))continue;
  const r=document.createRange();r.selectNodeContents(nd);const tops=new Set([...r.getClientRects()].filter(x=>x.width>0).map(x=>Math.round(x.top)));
  if(tops.size>1)out.push((el.className||el.tagName)+' :: '+t.slice(0,40))}
 document.querySelectorAll('#view *').forEach(e=>{if(e.offsetParent&&e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible'&&!e.matches('input,textarea,.tbl'))out.push('CLIP '+(e.className||e.tagName)+' :: '+e.textContent.trim().slice(0,30))});
 return [...new Set(out)]}"""
screens=[('home',"go('day');exitRun();setDate(today())"),('run',"openRun()"),('runList',"S.ui.run=today();render()"),('menu',"pkMenu('130')"),('menuClose',"closeSheet()"),('runDeliv',"exitRun();openRun()"),('meoff',"exitRun();setDate(addDays(today(),-1))"),('alloff',"setDate(addDays(today(),-2))"),
 ('locked',"setDate(addDays(today(),-7))"),('prep',"setDate(addDays(today(),1));openRun()"),('settle',"exitRun();S.ui.wv='settle';setSettle('this');go('week')"),('settleLast',"setSettle('last')"),('pay',"S.ui.wv='pay';render()"),
 ('fuel',"go('fuel')"),('stat',"go('stat')"),('set',"go('set')")]
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    for w in (320,390):
        pg=b.new_page(viewport={'width':w,'height':800},is_mobile=True,has_touch=True);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload();pg.evaluate(SEED)
        for name,fn in screens:
            pg.evaluate(fn);pg.wait_for_timeout(60)
            r=pg.evaluate(WRAP)
            if r: print(w,name,r)
            if len(sys.argv)>1: pg.screenshot(path=f'/tmp/pp_w_{w}_{name}.png',full_page=True)
    print('errors',errs);b.close()

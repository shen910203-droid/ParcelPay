import json
from playwright.sync_api import sync_playwright
store={}; calls=[]; fail={'on':False}
def handle(route):
    if fail['on']: return route.abort()
    b=json.loads(route.request.post_data); calls.append(b['action'])
    if b['token']!='t': return route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':False,'error':'密碼錯誤'}))
    if b['action']=='upsert':
        for it in b['items']:
            k=(it['type'],it['id']); 
            if k not in store or store[k]['updatedAt']<=it['data']['updatedAt']: store[k]=it['data']
        return route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True}))
    items=[{'type':k[0],'id':k[1],'data':v} for k,v in store.items()]
    return route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'items':items}))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(); ctx.route('https://script.google.com/**',handle)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/')
    pg.evaluate("setLocal('url','https://script.google.com/macros/s/X/exec');setLocal('token','t')")
    # phone A: offline entry
    fail['on']=True
    pg.evaluate("curDate='2026-11-23';render();setF('total','300');setF('start','130');setF('end','269')")
    pg.wait_for_timeout(2500)
    print('offline badge:',pg.inner_text('#badge'),'pending',pg.evaluate('S.pending.length'))
    fail['on']=False
    pg.evaluate("syncErr='';flush()"); pg.wait_for_timeout(1500)
    print('online badge:',pg.inner_text('#badge'),'store keys',list(store.keys()))
    # SW registered?
    pg.wait_for_timeout(1000); print('sw:',pg.evaluate("navigator.serviceWorker.controller?'active':'not yet'"))
    # phone B (new device): pull
    pg2=ctx.new_page(); pg2.goto('http://localhost:8765/')
    pg2.evaluate("setLocal('url','https://script.google.com/macros/s/X/exec');setLocal('token','t');pull(true)"); pg2.wait_for_timeout(1500)
    print('device B day:',pg2.evaluate("JSON.stringify(calc(getDay('2026-11-23')).delivered)"), pg2.evaluate("S.days['2026-11-23'].total"))
    # wrong token
    pg2.evaluate("setLocal('token','bad');syncErr='';pull(true)"); pg2.wait_for_timeout(800)
    print('bad token badge:',pg2.inner_text('#badge'))
    # offline reload with SW
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(800)
    print('offline reload title:',pg.title(), 'data kept:',pg.evaluate("S.days['2026-11-23'].end"))
    print('errors',errs); b.close()

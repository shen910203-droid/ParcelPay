from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:(print('  DIALOG:',d.message.replace('\n',' ')),d.accept()))
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    pg.evaluate("""()=>{const d=getDay(today());Object.assign(d,{total:'40',start:'100',end:'119',acStart:'90',acEnd:'125',multi:[{id:'m',no:105,qty:2,at:1}],skip:[{id:'s',no:110,at:1}],t:{leave:'',arrive:'06:00',start:'07:00',end:'',home:''}});touch('days',d);openRun()}""")
    C=lambda: json.loads(pg.evaluate("JSON.stringify((({assigned,delivered})=>({assigned,delivered}))(calc(getDay(today()))))"))
    print('rows:',pg.evaluate("pkRows(getDay(today())).map(r=>r.key).join(' ')"));print('calc',C())
    print('stat:',pg.inner_text('.plstat'))
    # tick 100..104
    for k in ['100','101','102','103','104']: pg.locator(f'.pr:has(b:text-is("{k}"))').tap()
    print('after 5 ticks first rows:',pg.evaluate("[...document.querySelectorAll('.pr b')].slice(0,3).map(x=>x.textContent).join(' ')"),'| last:',pg.inner_text('.lastbar').replace('\n',' '))
    pg.tap('.lastbar button'); print('cancel last →',pg.evaluate("pkRow(getDay(today()),'104').st||'todo'"))
    # plus on 100 (ticked) -> 100-1,100-2 ; tick carried?
    pg.evaluate("pkDo('100','plus')"); print('after plus 100:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.n===100).map(r=>r.key+':'+(r.st||'-')).join(' ')"),C())
    pg.evaluate("pkDo('100-2','plus')"); print('after plus again:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.n===100).map(r=>r.key+':'+(r.st||'-')).join(' ')"),C())
    pg.evaluate("pkDo('100-3','ret',0)"); print('100-3 returned:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.n===100).map(r=>r.key+':'+(r.st||'-')).join(' ')"),C())
    pg.evaluate("pkDo('111','miss')"); print('111 miss',C())
    pg.evaluate("pkDo('111','clear')"); print('111 clear',C(),'missing arr',pg.evaluate("getDay(today()).missing.length"))
    pg.evaluate("pkDo('105-2','minus')"); print('minus 105:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.n===105).map(r=>r.key).join(' ')"),C())
    # quick buttons interplay: quick multi on 101 (ticked) should keep tick on 101-1
    pg.fill('#qno','101');pg.tap('.qbtn >> text=多件 +1');print('quick +1 on ticked 101:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.n===101).map(r=>r.key+':'+(r.st||'-')).join(' ')"))
    pg.evaluate("qClear();plRefresh()")
    # quick return without pk
    pg.fill('#qno','112');pg.tap('.qbtn >> text=退件');pg.tap('#qreason >> text=拒收');print('quick return 112:',pg.evaluate("pkRow(getDay(today()),'112').st"),C())
    # filter
    pg.fill('#qno','11');pg.wait_for_timeout(100);print('filter 11 rows:',pg.evaluate("[...document.querySelectorAll('.pr b')].map(x=>x.textContent).join(' ')"))
    pg.evaluate("qClear();plRefresh()")
    # menu: note + photo
    pg.locator('.pr:has(b:text-is("102")) .more').tap(); pg.fill('#pknote','放後門'); pg.tap('.topsheet >> text=儲存')
    pg.set_input_files('.photobtn input','tests/test.jpg'); pg.wait_for_timeout(1500)
    print('photo stored:',pg.evaluate("(getDay(today()).pk['102']||{}).ph"),'thumbs:',pg.locator('#thumbs img').count())
    pg.screenshot(path='/tmp/pp_pk_menu.png')
    pg.tap('.shead >> text=關閉')
    # tick remaining & check alignment
    pg.evaluate("pkRows(getDay(today())).filter(r=>!r.st).forEach(r=>pkTap(r.key))")
    print('all ticked stat:',pg.inner_text('.plstat'),C())
    pg.screenshot(path='/tmp/pp_pk_list.png',full_page=True)
    # untick one and press 送完
    pg.evaluate("pkTap('119')"); pg.tap('text=✓ 送完')
    # purge old photo
    pg.evaluate("""async()=>{await PDB.put({id:'old',date:'2026-11-01',key:'x',blob:new Blob(['a']),at:Date.now()-15*864e5});await purgePhotos()}""")
    print('old purged:',pg.evaluate("PDB.get('old').then(r=>!r)"))
    # persistence after reload
    pg.reload();print('after reload ticks:',pg.evaluate("pkRows(getDay(today())).filter(r=>r.st==='ok').length"))
    # locked: tap does nothing
    pg.evaluate("const d=getDay(today());d.locked=true;touch('days',d);openRun()"); print('locked run?',pg.evaluate('S.ui.run'))
    print('errors',errs);b.close()

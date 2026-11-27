# v5.9：真正的核對、同事休假、單價依日期、固定成本、多件+1、時間提醒、缺件+退件提醒、發薪日當天
from playwright.sync_api import sync_playwright
JS = r"""()=>{const R={},T=(k,got,exp)=>R[k]=JSON.stringify(got)===JSON.stringify(exp)?'OK':`FAIL got ${JSON.stringify(got)} expect ${JSON.stringify(exp)}`;
 const mk=(dt,o)=>{const d=newDay(dt);Object.assign(d,o);return d};
 // 1. 核對：沒填 → 未核對；填對 → ok；填錯 → diff
 let d=mk('2026-11-20',{total:'300',start:'1',end:'150',fReturns:[{id:'f',qty:5,reason:'x'}]});
 T('none',calc(d).chk,'none');T('noFalseOK',sumTable(calc(d)).includes('核對相符'),false);
 d.fSay='145';T('ok',calc(d).chk,'ok');
 d.fSay='140';let c=calc(d);T('diff',[c.chk,c.chkBad[0].calc-c.chkBad[0].said],['diff',5]);
 d.fSay='145';d.fSayRet='4';T('retDiff',calc(d).chk,'diff');d.fSayRet='5';T('retOk',calc(d).chk,'ok');
 // 範圍填錯：以前會顯示對得上，現在要抓到
 d=mk('2026-11-20',{total:'300',start:'1',end:'160',fSay:'145',fReturns:[{id:'f',qty:5,reason:'x'}]});T('catchRange',calc(d).chk,'diff');
 // 支援：Frankie 說 130、支援說 129 → 跟 test_sup2 一樣應該相符
 d=mk('2026-11-25',{total:'373',start:'1',end:'100',multi:[{id:'m',no:5,qty:10}],returns:[1,2,3].map(n=>({id:'r'+n,no:n,qty:1,reason:'x'})),fReturns:[{id:'f',qty:5,reason:'x'}],sup:{on:true,name:'Bruce',fDel:'130',sRet:'',sDel:'129'}});
 c=calc(d);T('supOk',[c.delivered,c.fDelivered,c.sDelivered,c.chk],[106,130,129,'ok']);
 d.sup.sDel='127';T('supDiff',calc(d).chk,'diff');
 // 2. Frankie 休假：只有我 → 剩下應為 0
 d=mk('2026-11-21',{total:'152',start:'1',end:'150',missing:[{id:'a',no:500,qty:2}],fOff:true});c=calc(d);T('fOffOk',[c.fDelivered,c.left,c.chk],[0,0,'ok']);
 d.total='155';c=calc(d);T('fOffDiff',[c.left,c.chk],[3,'diff']);
 d=mk('2026-11-21',{total:'300',start:'1',end:'150',fOff:true,sup:{on:true,name:'Bruce',fDel:'',sRet:'2',sDel:'148'}});c=calc(d);T('fOffSup',[c.fDelivered,c.sDelivered,c.chk],[0,148,'ok']);
 T('fOffNoLockNag',c.warn.some(w=>w.includes('要填')),false);
 // 3. 單價依日期：舊的日子不變
 S.settings.rate=2.5;S.settings.rates=[{id:'r',from:'2027-01-08',rate:2.8}];
 const a=calc(mk('2027-01-07',{start:'1',end:'100'})).pay,b=calc(mk('2027-01-08',{start:'1',end:'100'})).pay;T('rate',[a,Math.round(b*100)/100],[250,280]);S.settings.rates=[];
 // 4. 固定成本：房租每週 200、車租每月 520（=120/週）
 S.settings.fixed=[{id:'h',label:'房租',amt:200,per:'w',from:''},{id:'c',label:'車租',amt:520,per:'m',from:''}];
 T('fixedWeek',Math.round(fixedWeek('2026-11-16')*100)/100,320);
 S.settings.fixed.push({id:'h2',label:'房租',amt:250,per:'w',from:'2026-11-23'});
 T('fixedReplace',[Math.round(fixedWeek('2026-11-16')),Math.round(fixedWeek('2026-11-23'))],[320,370]);
 S.settings.fixed=[];
 // 5. 多件 +1：已退 2 件的號碼按一次就變 3 件
 curDate='2026-11-22';const dd=getDay(curDate);Object.assign(dd,{total:'100',start:'1',end:'10',returns:[{id:'x',no:5,qty:2,reason:'x'}]});touch('days',dd);
 go('day');openRun();document.getElementById('qno').value='5';qAct('multi');T('multiPlus',pkQ(getDay(curDate),5),3);exitRun();
 // 6. 時間提醒：只提醒，照算
 d=mk('2026-11-22',{start:'1',end:'10',t:{leave:'07:00',arrive:'07:30',start:'15:00',end:'09:00',home:'16:00'}});c=calc(d);T('timeWarn',[c.deliver,c.warn.some(w=>w.startsWith('送貨 18h'))],[1080,true]);
 d=mk('2026-11-22',{start:'1',end:'10',t:{leave:'05:00',arrive:'05:30',start:'09:00',end:'15:00',home:'15:30'}});T('sortWarn',calc(d).warn.some(w=>w.startsWith('理貨 3h30m')),true);
 d=mk('2026-11-22',{start:'1',end:'10',t:{leave:'05:00',arrive:'05:30',start:'07:00',end:'15:00',home:'15:30'}});T('noTimeWarn',calc(d).warn.length,0);
 // 7. 缺件+退件提醒：清單裡 100-1 缺、100-2 退不提醒；輸入框兩筆才提醒（新文字）
 d=mk('2026-11-22',{start:'95',end:'105',multi:[{id:'m',no:100,qty:2}],missing:[{id:'a',no:100,qty:1,pk:'100-1'}],returns:[{id:'b',no:100,qty:1,reason:'x',pk:'100-2'}]});T('pkNoWarn',calc(d).warn.length,0);
 d=mk('2026-11-22',{start:'95',end:'105',missing:[{id:'a',no:100,qty:1}],returns:[{id:'b',no:100,qty:1,reason:'x'}]});T('quickWarn',calc(d).warn[0]||'', '100 在輸入框記了缺件又記了退件，系統當成 100 有 2 件。如果只有 1 件，請刪掉其中一筆');
 return R}"""
PAY = r"""()=>{localStorage.clear();S.days={};S.weeks={};const t=today(),ws=addDays(weekStart(t),-14);
 const d=getDay(ws);Object.assign(d,{total:'100',start:'1',end:'50'});touch('days',d);
 const r=wkGet(ws);r.pd=t;wkSave(r);S.ui.wv='pay';go('week');
 return {next:document.querySelector('.card .mid').textContent,owedRed:document.querySelectorAll('.card .mid.badc').length}}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('dialog',lambda dl:dl.accept())
    pg.goto('http://localhost:8765/');pg.evaluate("localStorage.clear()");pg.reload()
    print('version',pg.evaluate("APP_VERSION"))
    for k,v in pg.evaluate(JS).items(): print(k,v)
    print('payday today',pg.evaluate(PAY),'期望 next=今天發薪, owedRed=0')
    print('errors',errs);b.close()

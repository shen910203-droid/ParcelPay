/**
 * ParcelPay 送貨本 — Google Sheets 同步後端
 * 設定步驟：
 * 1. 開一個新的 Google 試算表 → 擴充功能 → Apps Script
 * 2. 刪掉預設內容，貼上這整個檔案
 * 3. 把下面 TOKEN 改成你自己的密碼（英數混合、長一點）
 * 4. 部署 → 新增部署作業 → 類型選「網頁應用程式」
 *    執行身分：我 ／ 誰可以存取：所有人 → 部署 → 授權
 * 5. 複製「網頁應用程式網址」（/exec 結尾），貼到 ParcelPay ⚙️設定，密碼填同一組
 * 之後若修改此程式碼：部署 → 管理部署作業 → 編輯 → 版本選「新版本」，網址不變
 */
const TOKEN = '改成你自己的密碼';

const COLS = {
  days:     ['id','updatedAt','deleted','日期','帳號總件數','範圍','我送達','我薪資','我退件','Frankie送達','Frankie退件','缺件','多件','退件明細','公里','油錢','發薪日','備註','json'],
  fuel:     ['id','updatedAt','deleted','日期','金額','公升','TripA','油價','km/L','備註','json'],
  weeks:    ['id','updatedAt','deleted','週起','發薪日','實際入帳','備註','json'],
  settings: ['id','updatedAt','deleted','json']
};
const NAMES = { days:'每日', fuel:'加油', weeks:'每週入帳', settings:'設定' };

function doGet() {
  return ContentService.createTextOutput('送貨本 API OK');
}

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return out({ ok:false, error:'格式錯誤' }); }
  if (body.token !== TOKEN) return out({ ok:false, error:'密碼錯誤' });
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    if (body.action === 'pull')   return out({ ok:true, items: pullAll() });
    if (body.action === 'upsert') { (body.items || []).forEach(upsert); return out({ ok:true, n:(body.items||[]).length }); }
    return out({ ok:false, error:'未知動作' });
  } catch (err) {
    return out({ ok:false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function sheetOf(type) {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(NAMES[type]);
  if (!sh) {
    sh = ss.insertSheet(NAMES[type]);
    sh.getRange(1, 1, 1, COLS[type].length).setValues([COLS[type]]).setFontWeight('bold');
    sh.setFrozenRows(1);
    sh.getRange('A:A').setNumberFormat('@');           // id 保持文字，避免被轉成日期
    sh.hideColumns(COLS[type].length);                   // 隱藏 json 欄
  }
  return sh;
}

function upsert(it) {
  if (!COLS[it.type]) return;
  const cols = COLS[it.type];
  const sh = sheetOf(it.type);
  const last = sh.getLastRow();
  const ids = last > 1 ? sh.getRange(2, 1, last - 1, 2).getValues() : [];
  let rowIdx = -1;
  for (let i = 0; i < ids.length; i++) if (idStr(ids[i][0]) === String(it.id)) { rowIdx = i + 2; break; }
  const d = it.data || {};
  if (rowIdx > 0 && Number(ids[rowIdx - 2][1]) > Number(d.updatedAt || 0)) return; // 雲端較新，不覆蓋
  const s = it.summary || {};
  const row = cols.map(c => {
    if (c === 'id') return String(it.id);
    if (c === 'updatedAt') return d.updatedAt || 0;
    if (c === 'deleted') return d.deleted ? 'Y' : '';
    if (c === 'json') return JSON.stringify(d);
    return s[c] == null ? '' : s[c];
  });
  if (rowIdx < 0) rowIdx = sh.getLastRow() + 1;
  sh.getRange(rowIdx, 1).setNumberFormat('@');          // id 一律當文字
  sh.getRange(rowIdx, 1, 1, row.length).setValues([row]);
}

// 萬一 id 被 Sheets 轉成日期，轉回 yyyy-MM-dd
function idStr(v) {
  if (v instanceof Date) return Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  return String(v);
}

function pullAll() {
  const items = [];
  Object.keys(COLS).forEach(type => {
    const sh = SpreadsheetApp.getActive().getSheetByName(NAMES[type]);
    if (!sh || sh.getLastRow() < 2) return;
    const n = COLS[type].length;
    const vals = sh.getRange(2, 1, sh.getLastRow() - 1, n).getValues();
    vals.forEach(r => {
      try { items.push({ type, id: idStr(r[0]), data: JSON.parse(r[n - 1]) }); } catch (e) {}
    });
  });
  return items;
}

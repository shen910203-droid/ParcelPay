# ParcelPay 送貨本 — 專案交接說明（給 Claude Code）

這份檔案讓新的 Claude 對話直接接手，不用重新問背景。改功能前先讀完。

## 使用者：Aiden
- 台灣人，目前在澳洲（Brisbane 時區 UTC+10）打工度假，做**快遞送貨**，按件計薪。
- 同事 **Frankie**，兩人送同一區、貨掃到同一個帳號；偶爾有**支援人員**（例如 Bruce）。
- **一律用繁體中文回覆**。
- 溝通偏好：
  - 直接、具體、用實際數字舉例；長期風險和限制要一開始就講。
  - 他常說「**先文字回覆 / 先跟我討論**」→ 這時**只回文字，不要改程式**。
  - 他回報「數字不對」時，**先確認是資料輸入問題還是程式 bug，再決定要不要改**（曾經因為沒先問就改壞，v5.4 → v5.5 還原）。
  - 每次推新版，回覆裡要寫明版本號（他會到「設定」頁最下面核對）。
  - Git / GitHub 新手：涉及 git 操作要從頭解釋；由 Claude 負責 commit + push。
  - 開發偏好：純 HTML + JS 單一檔案、深色現代 UI、不要需要安裝的框架。

## 部署
- Repo：`shen910203-droid/parcelpay`（public），`main` 分支 = GitHub Pages。
- 網址：https://shen910203-droid.github.io/parcelpay/ （他在 iPhone 上「加入主畫面」當 App 用）。
- push 後 GitHub Actions 部署約 40–60 秒；可用
  `gh api "repos/shen910203-droid/parcelpay/actions/runs?per_page=1" --jq '.workflow_runs[]|[.status,.conclusion,.head_sha[0:7]]|@tsv'` 確認。
- **每次改版必做**：
  1. `index.html` 裡 `const APP_VERSION='vX.Y'` 加一版。
  2. `sw.js` 裡 `const CACHE='parcelpay-vX.Y'` 同步改。
  3. commit 訊息用中文寫「vX.Y：做了什麼」。
- 目前版本：**v5.9**（真正的件數核對、同事休假、單價依生效日期、固定成本項目、時間提醒、發薪日當天不標紅、輸入框多件 +1 修正）。
- 手機更新：關掉 App 重開；卡住就按「設定 → 最下面 → 強制更新」（只清程式快取，不刪資料）。

## 檔案
| 檔案 | 用途 |
|---|---|
| `index.html` | 整個 App（HTML+CSS+JS 單一檔，約 1100 行） |
| `sw.js` | Service Worker：network-first（`cache:'no-store'`），離線時用快取；新版自動 reload |
| `apps-script.gs` | Google Apps Script 後端（使用者貼在自己的 Google 試算表裡），`doPost` 處理 `pull` / `upsert`，用 TOKEN 驗證 |
| `manifest.webmanifest`、`icon*.png`、`icon.svg`、`apple-touch-icon.png` | PWA 圖示 |
| `tests/` | Playwright 回歸測試（見下方） |

## 資料與同步
- 全部狀態在 `S`（localStorage key `songhuoben_v1`）：`days`、`fuel`、`weeks`、`settings`、`pending`（待上傳佇列）、`local`（Apps Script 網址、密碼、`autoSync`，只存本機不同步）、`ui`。
- 每筆紀錄有 `id`、`updatedAt`、`deleted`；同步用「updatedAt 較新者勝」合併。`touch(type,rec)` = 更新時間 + 存檔 + 排入同步。
- 照片存 **IndexedDB**（`parcelpay-photos`），壓縮到 1280px JPEG，**14 天自動刪除**，**不上傳雲端**；day 紀錄裡只存照片 id。
- 自動同步開關（設定頁）：關閉時只存手機，手動按「立即同步」。
- 使用者已接通 Google Sheets（畫面顯示「已同步」）。

### Day 紀錄主要欄位
v5.9 新增：`fSay`（Frankie 說他送達，沒支援時用；有支援時用 `sup.fDel`）、`fSayRet`（Frankie 說他退件）、`fOff`（Frankie 休假）、`sup.sDel`（支援說他送達）。

`date, total(總件數), start, end(我的範圍), missing[{no,qty,pk?}], multi[{no,qty}], returns[{no,qty,reason,pk?}], fReturns[{qty,reason}], skip[{no}], pk{ "100" | "100-2": {st:'ok',at,note,ph[]} }, t{leave,arrive,start,end,home,eLeave,eArrive,eDone,eHome}, mode(''|'evening'), kmB, kmBe, sup{on,name,fDel,sRet}, offType(''|'me'|'all'), offMiss, ded[{amount,note,confirmed}], acStart, acEnd, locked, note`

### Week 紀錄（`S.weeks[週一日期]`，v5.8 起）
`id(週一), pd(自訂發薪日，空字串 = 用預設), pays[{id,date,amt,st:'in'|'wait',note}], extras[{id,label,amt,date}], received(=已入帳合計，舊欄位保留給相容與試算表), note`
- 讀取一律用 `wkRec(ws)`：舊資料只有 `received` 時會自動轉成一筆 `legacy` 入帳。
- 發薪日一律用 `wkPd(ws)`（有 `pd` 用 `pd`，否則 `payday(ws)`），不要直接用 `payday()`。

## 計算規則（`calc(d)`，改之前一定要理解）
- **每個號碼的件數** = max(標記的多件數, 該號缺件數 + 退件數)。所以同一號直接退 2 件會自動當 2 件。
- 範圍號碼數 = `end − start + 1 − 範圍內跳號數`；`extra` = 範圍內每號 (件數−1) 的加總；`assigned`(今日拿貨) = 號碼數 + extra。
- **我送達** = assigned − 我範圍缺件 − 我退件；薪資 = 送達 × `rateOn(date)`。
- **單價依生效日期**（v5.9）：`settings.rate` = 起始單價（$2.5），`settings.rates=[{id,from,rate}]` = 從某天開始的新單價。一律用 `rateOn(date)`，**不要直接用 `settings.rate`**，否則改單價會改到舊帳。Frankie 單價跟我一樣。
- **三個人**：我、Frankie、支援。組合：我+Frankie（平常）／Frankie 休（`fOff`，只有我，可加支援）／我休（`offType:'me'`，Frankie+支援）／全休（`'all'`）。
- **Frankie 休假**（`fOff`）：Frankie = 0、退件 = 0；沒支援時「剩下 = 總件數 − 我 assigned − 範圍外缺件」應該是 0；有支援時支援 = 總件數 − 我 assigned − 範圍外缺件 − 支援退件。
- **核對**（v5.9，`calc().chk` = ok / diff / none / na）：Frankie 和支援每天會**親口說**送達、退件數，拿來跟倒推結果比。舊版「送達+退件+缺件 = 總件數」是恆等式、永遠成立，**不能拿來當核對**。沒支援比 `fSay` vs Frankie 倒推；有支援比 `sup.sDel` vs 支援倒推；`fSayRet` vs 記錄的 Frankie 退件；Frankie 休假沒支援比「剩下 = 0」。沒填 → 「未核對」，結算鎖定時提醒。
- **同事平均提醒**（`dayWarn`）：Frankie 倒推件數比他最近 14 天平均多或少一半以上 → 提醒。放在 `calc` 外面，因為要讀其他天（避免 calc 互相呼叫）。
- **時間提醒**：理貨 > 3h、送貨 > 14h、單趟通勤 > 2h → 提醒「時間對嗎？」，**只提醒、照算**，使用者確認過真的這麼久就不管。
- **Frankie 送達**（無支援）= 總件數 − 我的 assigned − 範圍外缺件 − Frankie 退件。
- **有支援**：`sup.fDel` 是 **Frankie 實際送達件數（不含退件）**，支援 = 總件數 − 我 assigned − 範圍外缺件 − Frankie 送達 − Frankie 退件 − 支援退件。⚠️ v5.4 曾改成「含退件」，使用者表示錯，已還原，**不要再改**。
- **我休假**（`offType:'me'`）：我 = 0，其他人照上面倒推，缺件用 `offMiss` 數字。**全員休息**（`'all'`）：不計。
- **跳號** = 系統根本沒有這個號碼（不同於缺件 = 有派單但倉庫點不到）。
- 同一號在**輸入框**記了缺件又記退件（沒有 `pk`）→ 系統當成該號 2 件，提醒使用者。逐件清單裡 100-1 缺、100-2 退（有 `pk`）是正常的，不提醒。使用者平常在逐件清單操作。
- **固定成本**（v5.9）：`settings.fixed=[{id,label,amt,per:'w'|'m',from}]`（房租按週、車租按月；每月 ×12÷52 換成每週）。**每週都扣，沒上班也扣**；按天攤（`fixedOnDay`）。同名項目以最近開始的為準（漲價 = 新增同名新金額；停付 = 同名 $0）。舊的 `weeklyFixed` 自動當成一個項目。發薪/入帳頁從第一筆紀錄那週起每週都列（有固定成本時）；統計頁按天數比例；時薪計算器把當週成本平均分到當週上班日。
- **扣款** `ded`：「待確認」不扣錢，「已扣」才從當週應領扣掉。
- 「已過發薪日未入帳」從發薪日**隔天**才算（當天顯示「今天發薪」，不標紅）。
- **一週 = 週一～週日**，發薪日預設 = 週一 + 13 天（下週日，`settings.payOffset`），整週一起發；結算頁點「發薪 ✎」可只改單一週的發薪日。
- **應領合計** = 件數薪資 − 已扣款 + 補貼獎金（`extras`）。**已入帳** = `pays` 裡 `st:'in'` 加總；**待核准** = `st:'wait'` 加總（會計還沒核准的先記這個，錢進來點一下改成已入帳）。**差額** = 已入帳 + 待核准 − 應領合計。「已過發薪日未入帳」= 發薪日已過且 應領 − 已入帳 > 0 的週。
- **時間**：早上領貨 → 理貨 = 到倉庫→開始送貨；前一晚領貨（`mode:'evening'`，紀錄存在「送貨那天」）→ 理貨 = 晚上到倉庫→點完離開；通勤 = 所有往返加總；送貨 = 開始送貨→送完。`件/時` = 送達 ÷ 送貨時間。
- **油錢**：長期油耗（加滿時記 Trip A 與公升，沒加滿的公升併入下一次加滿）× 當天之前最近一次加油的油價 × 當天 Trip B 公里。
- 有 `locked` 的日子不能改（扣款除外）；結算表的未送 = 退件 + 缺件。

## 畫面結構
- 底部分頁：今日 / 結算（結算表、發薪入帳：每週可「＋ 入帳」分批記、「＋ 補貼 / 獎金」）/ 油錢 / 統計（含時薪計算器，可勾分子分母）/ 設定。
- **今日頁**：週日期列 → 首頁統計表（我/Frankie/支援/合計，算法可展開，`$` 按鈕可隱藏金額）→ 流程大按鈕（出門→到倉庫→開始送貨→送完→到家；出門時提醒 B 歸零，到家時輸入 B）→ 今天進度 → 紀錄（退件/缺件/多件/跳號/Frankie 範圍，可收合）→ 收工後 → 當日結算完成（鎖定）→ 扣款。
- **送貨模式**（`S.ui.run`，全螢幕、關掉 App 重開會回來）：今日拿貨、全帳號核對（前一晚預標多件用）、範圍、輸入編號 + 缺件/多件+1/退件/跳號、**逐件清單**（點一下打勾、送完沉到下面、「最近送達」可取消、⋯ 選單：送達/退件/缺件/+1/移除/跳號/備註/拍照）。

## iPhone Safari 踩過的坑（改 UI 時注意）
- 時間 / 日期滾輪：用 `onblur` 存，**不要用 onchange 觸發 render**（會轉到一半就跳掉）。
- 打字時藏底部導覽列（`body.typing`）；元素被重畫移除時 Safari 不發 focusout → 用 `clearTyping()` 補救。
- 從下方滑出的面板會被鍵盤擋 → 選單一律從上方出（`.topsheet`），隱藏時連陰影一起藏。
- `confirm('...\n...')` 寫在 HTML 的 onclick 屬性裡時，不能有真的換行字元（會語法錯誤）。
- 雙擊放大：`touch-action:manipulation`；input 字級 ≥ 16px 避免自動放大。
- class 名稱小心衝突（曾經 `.ev` / `.x` 同時用在按鈕和列表，樣式互相污染）。
- 字級只用 12 / 14 / 16 / 20 / 24 / 40（輸入編號框 28）。

## 測試（改完一定要跑）
使用者的電腦是 **Windows**（Claude Code 在本機跑，不是雲端）。Python 3.12 在 `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`（`python` 指令是 Microsoft Store 空殼，不能用），Playwright + Chromium 已裝好。git 在 `C:\Program Files\Git\cmd\git.exe`。
```powershell
powershell -ExecutionPolicy Bypass -File tests\run_all.ps1
```
（Linux / Mac：`bash tests/run_all.sh`）
- `test_v59.py`：v5.9 的核對、同事休假、單價、固定成本、多件 +1、時間提醒、發薪日當天，每項應該印 OK。
- 已知舊問題：320 寬時送貨模式那行「範圍 139 號 · 多件 +2 · 缺件 −1 · 退件 −1」會換行（v5.8 就有）。
- 測試會在 8765 埠起本機伺服器，用 Playwright 模擬手機（320 / 390 寬）。
- `test_wrap.py`：掃全部畫面找**換行或被截斷的文字**、超出畫面、元素重疊 —— 使用者很在意版面整齊，輸出應該是空的。
- `test_pk.py`：逐件清單、+1/−1、退件、照片；`test_eve.py`：前一晚領貨時間；`test_sup2.py`：支援計算（應為 106 / 130 / 129 / 373）。
- 部分測試的「期望」文字是舊版寫的，看實際數字是否合理即可。
- 也可以用 Playwright 截圖後自己看圖檢查版面。

## 還沒做 / 討論過的點子
- 休息暫停打卡（件/時目前包含中途休息時間）。
- 首頁統計表的退件、缺件仍分開（結算表已合併成「未送」）。
- iPhone 推播通知做不到（需推播伺服器）；已改成 App 內按出門時提醒。

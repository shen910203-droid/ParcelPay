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
- 目前版本：**v5.7**。
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
`date, total(總件數), start, end(我的範圍), missing[{no,qty,pk?}], multi[{no,qty}], returns[{no,qty,reason,pk?}], fReturns[{qty,reason}], skip[{no}], pk{ "100" | "100-2": {st:'ok',at,note,ph[]} }, t{leave,arrive,start,end,home,eLeave,eArrive,eDone,eHome}, mode(''|'evening'), kmB, kmBe, sup{on,name,fDel,sRet}, offType(''|'me'|'all'), offMiss, ded[{amount,note,confirmed}], acStart, acEnd, locked, note`

## 計算規則（`calc(d)`，改之前一定要理解）
- **每個號碼的件數** = max(標記的多件數, 該號缺件數 + 退件數)。所以同一號直接退 2 件會自動當 2 件。
- 範圍號碼數 = `end − start + 1 − 範圍內跳號數`；`extra` = 範圍內每號 (件數−1) 的加總；`assigned`(今日拿貨) = 號碼數 + extra。
- **我送達** = assigned − 我範圍缺件 − 我退件；薪資 = 送達 × `settings.rate`（$2.5）。
- **Frankie 送達**（無支援）= 總件數 − 我的 assigned − 範圍外缺件 − Frankie 退件。
- **有支援**：`sup.fDel` 是 **Frankie 實際送達件數（不含退件）**，支援 = 總件數 − 我 assigned − 範圍外缺件 − Frankie 送達 − Frankie 退件 − 支援退件。⚠️ v5.4 曾改成「含退件」，使用者表示錯，已還原，**不要再改**。
- **我休假**（`offType:'me'`）：我 = 0，其他人照上面倒推，缺件用 `offMiss` 數字。**全員休息**（`'all'`）：不計。
- **跳號** = 系統根本沒有這個號碼（不同於缺件 = 有派單但倉庫點不到）。
- 首頁總件數核對：送達合計 + 退件合計 + 缺件合計 = 總件數。
- **扣款** `ded`：「待確認」不扣錢，「已扣」才從當週應領扣掉。
- **一週 = 週一～週日**，發薪日 = 週一 + 13 天（下週日），整週一起發。
- **時間**：早上領貨 → 理貨 = 到倉庫→開始送貨；前一晚領貨（`mode:'evening'`，紀錄存在「送貨那天」）→ 理貨 = 晚上到倉庫→點完離開；通勤 = 所有往返加總；送貨 = 開始送貨→送完。`件/時` = 送達 ÷ 送貨時間。
- **油錢**：長期油耗（加滿時記 Trip A 與公升，沒加滿的公升併入下一次加滿）× 當天之前最近一次加油的油價 × 當天 Trip B 公里。
- 有 `locked` 的日子不能改（扣款除外）；結算表的未送 = 退件 + 缺件。

## 畫面結構
- 底部分頁：今日 / 結算（結算表、發薪入帳）/ 油錢 / 統計（含時薪計算器，可勾分子分母）/ 設定。
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
```bash
pip install playwright pillow && python -m playwright install chromium
bash tests/run_all.sh
```
- 測試會在 8765 埠起本機伺服器，用 Playwright 模擬手機（320 / 390 寬）。
- `test_wrap.py`：掃全部畫面找**換行或被截斷的文字**、超出畫面、元素重疊 —— 使用者很在意版面整齊，輸出應該是空的。
- `test_pk.py`：逐件清單、+1/−1、退件、照片；`test_eve.py`：前一晚領貨時間；`test_sup2.py`：支援計算（應為 106 / 130 / 129 / 373）。
- 部分測試的「期望」文字是舊版寫的，看實際數字是否合理即可。
- 也可以用 Playwright 截圖後自己看圖檢查版面。

## 還沒做 / 討論過的點子
- 休息暫停打卡（件/時目前包含中途休息時間）。
- 首頁統計表的退件、缺件仍分開（結算表已合併成「未送」）。
- iPhone 推播通知做不到（需推播伺服器）；已改成 App 內按出門時提醒。

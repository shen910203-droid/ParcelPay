# ParcelPay 送貨本

快遞件數、薪資、油錢、時薪的個人紀錄工具。單一 HTML 檔，資料同步到 Google Sheets。

- `index.html` — 主程式
- `apps-script.gs` — 貼到 Google Sheets 的 Apps Script（同步後端）
- `sw.js` — 離線支援（沒訊號也能打開）
- `manifest.webmanifest`、`icon*.png`、`icon.svg` — 加到主畫面用的 App 圖示

算法：
- 我送達 = (迄 − 起 + 1) + 同址多件 − 我範圍缺件 − 我退件
- Frankie 送達 = 帳號總件數 − 我範圍總件數 − Frankie 範圍缺件 − Frankie 退件
- 每日油錢 = Trip B km × 長期油耗(L/km) × 當天之前最近一次加油的油價
- 一週 = 週一～週日，發薪日 = 週一 + 13 天


開發交接說明請看 `CLAUDE.md`；回歸測試：`bash tests/run_all.sh`。

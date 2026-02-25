# OpenClaw 安裝與設定踩坑日誌

> 記錄凱文兄安裝 OpenClaw 時遇到的問題與解決方案

---

## 🔧 安裝/設定問題

### 1. Codex Agent 不被 Gateway 識別
- **問題**：新增 agent 後無法載入
- **狀態**：⚠️ 未完全解決

### 2. gogcli Windows keyring 問題
- **問題**：OAuth token 無法儲存，路徑錯誤
- **狀態**：⚠️ 未解決（可用 Gmail Skill 替代）

### 3. NotebookLM MCP 設定
- **問題**：無法直接寫入 OpenClaw config，需用 CLI 手動操作
- **參考**：https://www.meta-intelligence.tech/insight-openclaw-tutorial

---

## 🐛 系統問題（Recurring Failures）

### 4. read:EISDIR
- **問題**：vendor skill 路徑錯誤
- **錯誤路徑**：`C:\Users\junic\AppData\Roaming\npm\node_modules\openclaw\skills\vendor\SKILL.md`
- **正確路徑**：`C:\Users\junic\.openclaw\skills\vendor\SKILL.md`
- **狀態**：✅ 已修復

### 5. gateway:invalid config
- **問題**：設定檔問題
- **發生次數**：14次
- **狀態**：⚠️ 需持續觀察

### 6. web_search provider 偵測
- **問題**：Brave API Key 未明確設定
- **訊息**：`no provider configured, auto-detected "brave"`
- **狀態**：✅ 功能正常，但建議寫死設定

---

## 🌐 自動化問題

### 7. 華紙下載問題
- **問題**：openclaw profile 下載 Excel 回傳 HTML（不是 xlsx）
- **根因**：session/context 差異 + jquery.fileDownload cookie handshake
- **狀態**：✅ 可用 Chrome Relay 繞過

---

## 📝 待辦
- [ ] 解決 Codex Agent 載入問題
- [ ] 追蹤 gateway:invalid config
- [ ] 將 Brave Key 寫入設定檔

---

*Last updated: 2026-02-25*

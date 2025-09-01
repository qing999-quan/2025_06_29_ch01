# `stat_p_129` 多條件查詢腳本：逐行說明（Markdown）

> 版本：2025-09-01
> 功能：從 **環境部 stat\_p\_129** API 取資料 → 讓你多選 **統計區（縣市）** 與 **統計期區間** → 篩選 → 匯出 **CSV** 與 **Excel** 檔案。

---

## 快速使用

```bash
# 安裝相依（第一次才需要）
python -m pip install pandas openpyxl

# 執行
python stat_p129_query.py
```

互動範例：

```
可選擇的統計區：
1. 臺北市
2. 新北市
...
請輸入要查詢的統計區（可多選，以逗號分隔；可用『編號』或『名稱』）：1,新北市

=== 統計期區間輸入 ===
起始統計期：113-01
結束統計期：113-12
```

---

## 程式結構總覽

1. **匯入套件**：處理網路、JSON、日期、正則、資料表（pandas）、路徑。
2. **參數設定**：API URL、輸出資料夾。
3. **核心工具函式**：

   * `parse_period`：把「統計期」文字（西元/民國、多種格式）→ `datetime`。
   * `load_records`：呼叫 API 取得 JSON → `records`。
   * `normalize_df`：整理欄位、轉型別、加入 `period_dt`。
   * `prompt_multi_select`：互動式多選統計區。
   * `prompt_period_range`：輸入起訖統計期。
   * `filter_df`：依條件篩選。
   * `export_files`：輸出 CSV 與 Excel。
4. **`main()`**：把上述流程串起來。
5. **`if __name__ == "__main__":`**：作為可執行腳本的入口，外層錯誤處理。

---

## 逐行說明

> 下方以「**原程式碼**」→「**解說**」方式呈現；若是多行同一概念，會合併說明。

### 1) 匯入套件與參數

```python
import json
import ssl
import urllib.request
from datetime import datetime
import re
import pandas as pd
from pathlib import Path
```

* `json`：解析 API 回傳的 JSON。
* `ssl`、`urllib.request`：建立 HTTPS 連線與讀取資料。
* `datetime`：處理時間（建立統計期的 `datetime` 物件、檔名時間戳）。
* `re`：正則表達式，解析各種統計期格式。
* `pandas`：把資料變成表格、篩選、輸出。
* `Path`：友善、跨平台的路徑操作。

```python
URL = ("https://data.moenv.gov.tw/api/v2/stat_p_129"
       "?api_key=58d6040c-dca7-407f-a244-d0bfdfa8144a"
       "&limit=1000&sort=ImportDate%20desc&format=JSON")
OUT_DIR = Path(".")  # 輸出資料夾
```

* `URL`：

  * `limit=1000`：最多抓 1000 筆。
  * `sort=ImportDate desc`：以匯入時間新到舊排序。
  * `format=JSON`：指定回傳格式。
* `OUT_DIR`：輸出到目前資料夾（可改成其它路徑，例如 `Path(r"D:\exports")`）。

```python
context = ssl._create_unverified_context()
```

* 建立一個 SSL 連線環境；在某些環境中可避免憑證問題。

---

### 2) `parse_period(s)`：把統計期字串 → `datetime`

```python
def parse_period(s: str) -> datetime:
    """
    解析統計期字串為 datetime（以當月1日或當年1月1日代表）。
    支援：
      - 西元: 2024-07, 2024/07, 2024年07月, 2024, 2024年
      - 民國: 113-07, 113/07, 113年07月, 民國113/07, 113, 113年, 民國113年
    """
    s = s.strip().replace(" ", "")
```

* 去頭尾空白、移除中間空白，方便配對各種格式。

```python
    # 西元：YYYY-MM / YYYY/MM / YYYY年MM月
    for pat in [r"^(\d{4})[-/](\d{1,2})$", r"^(\d{4})年(\d{1,2})月$"]:
        m = re.match(pat, s)
        if m:
            y, mth = int(m.group(1)), int(m.group(2))
            return datetime(y, mth, 1)
```

* \*\*西元「年+月」\*\*兩種寫法：`YYYY-MM` / `YYYY/MM` / `YYYY年MM月`。
* 抓到就回傳該年該月的第 1 天（`datetime(y, mth, 1)`）。

```python
    # 西元只有年：YYYY 或 YYYY年 -> 視為該年1月
    m = re.match(r"^(\d{4})年?$", s)
    if m:
        y = int(m.group(1))
        return datetime(y, 1, 1)
```

* **西元只有年**（`YYYY` 或 `YYYY年`）→ 視為該年 **1 月**。

```python
    # 民國（先去掉前綴「民國」）
    s2 = re.sub(r"^民國", "", s)
```

* 有些資料會寫「民國113年」；先把「民國」兩字去掉再處理。

```python
    # 民國：YYY-MM / YYY/MM / YYY年MM月
    for pat in [r"^(\d{2,3})[-/](\d{1,2})$", r"^(\d{2,3})年(\d{1,2})月$"]:
        m = re.match(pat, s2)
        if m:
            roc_y, mth = int(m.group(1)), int(m.group(2))
            y = roc_y + 1911
            return datetime(y, mth, 1)
```

* **民國「年+月」**（`YYY-MM` / `YYY/MM` / `YYY年MM月`）。
* 先轉成西元：`西元年 = 民國年 + 1911`。

```python
    # 民國只有年：YYY 或 YYY年 -> 視為該年1月
    m = re.match(r"^(\d{2,3})年?$", s2)
    if m:
        y = int(m.group(1)) + 1911
        return datetime(y, 1, 1)
```

* **民國只有年**（`YYY` / `YYY年`）→ 視為該年 **1 月**。

```python
    # 緊湊格式：YYYYMM / YYYMM
    m = re.match(r"^(\d{4})(\d{2})$", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), 1)
    m = re.match(r"^(\d{3})(\d{2})$", s2)
    if m:
        return datetime(int(m.group(1)) + 1911, int(m.group(2)), 1)
```

* **緊湊格式**：`YYYYMM`（西元）或 `YYYMM`（民國）。

```python
    raise ValueError(f"無法解析統計期格式：{s}")
```

* 都配不到 → 丟錯給外層（外層會友善處理）。

> 想支援「**113年度**」？把兩處「只有年」的 `年?` 改成 `(年|年度)?` 即可。

---

### 3) 下載資料 `load_records(url)`

```python
def load_records(url: str) -> list[dict]:
    with urllib.request.urlopen(url, context=context) as resp:
        data = json.loads(resp.read().decode("utf-8-sig"))
    return data["records"]
```

* 建立 HTTP(S) 連線 → 讀回應 → 以 `utf-8-sig` 解碼（可去掉 BOM）。
* 取出關鍵的 `records` 欄位（一筆筆資料是 dict）。

---

### 4) 整理成表格 `normalize_df(records)`

```python
def normalize_df(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame.from_records(records)
    df = df[["item1", "item2", "value1", "value2", "value3", "value4", "value5"]].rename(
        columns={
            "item1": "統計期",
            "item2": "統計區",
            "value1": "總處理量",
            "value2": "回收再利用量",
            "value3": "焚化量",
            "value4": "衛生掩埋量",
            "value5": "其他處理量",
        }
    )
```

* `records (list[dict])` → `pandas.DataFrame`。
* 只保留用得到的欄位並改成 **中文易讀欄名**。

```python
    # 逐筆解析統計期；遇到異常不讓整個程式掛掉
    period_list = []
    bad_rows = 0
    for s in df["統計期"]:
        try:
            period_list.append(parse_period(str(s)))
        except Exception:
            period_list.append(pd.NaT)
            bad_rows += 1

    df["period_dt"] = pd.to_datetime(period_list)

    if bad_rows:
        print(f"⚠ 注意：有 {bad_rows} 筆統計期格式無法解析，已略過（period_dt=NaT）。")

    # 去除 period_dt 無法解析者，避免之後排序/篩選報錯
    df = df.dropna(subset=["period_dt"]).copy()
```

* 逐筆把「統計期」轉成 `datetime` 放到新欄位 `period_dt`。
* 解析失敗（奇怪格式）就設成 `NaT`，並計數、提示；再把它們先丟掉。

```python
    # 數值轉數字
    for col in ["總處理量", "回收再利用量", "焚化量", "衛生掩埋量", "其他處理量"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
```

* 將數值欄轉成數字（遇到非數字字串 → `NaN`）。

---

### 5) 多選統計區 `prompt_multi_select`

```python
def prompt_multi_select(options: list[str], title: str) -> list[str]:
    """
    顯示選單，支援輸入編號清單（如 1,3,5）或直接輸入名稱（如 台北市,新北市）
    回傳所選名稱列表。
    """
    print(f"\n可選擇的{title}：")
    for idx, name in enumerate(options, 1):
        print(f"{idx}. {name}")
    raw = input(f"\n請輸入要查詢的{title}（可多選，以逗號分隔；可用『編號』或『名稱』）：").strip()

    if not raw:
        return []

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    selected = set()

    # 先嘗試把每個片段當作編號
    for p in parts:
        if p.isdigit() and 1 <= int(p) <= len(options):
            selected.add(options[int(p) - 1])
        else:
            # 視為名稱匹配（全名）
            if p in options:
                selected.add(p)
            else:
                # 嘗試模糊包含
                hit = [opt for opt in options if p in opt]
                if hit:
                    selected.update(hit)
                else:
                    print(f"⚠ 找不到：{p}")

    return list(selected)
```

* 顯示可選項目與編號（從 1 開始）。
* 支援 **編號**、**完整名稱**、**模糊包含**（如「北市」→「臺北市」）。
* 回傳去重後的清單。

---

### 6) 輸入統計期區間 `prompt_period_range`

```python
def prompt_period_range() -> tuple[datetime | None, datetime | None]:
    print("\n=== 統計期區間輸入 ===")
    print("輸入格式範例：")
    print("  西元：2024-05 或 2024/05 或 2024年05月")
    print("  民國：113-05 或 113/05 或 113年05月 或 民國113/05")
    print("若不想限制起/迄其一，可直接按 Enter 跳過。")
    s_from = input("起始統計期：").strip()
    s_to = input("結束統計期：").strip()

    def try_parse(x):
        if not x:
            return None
        return parse_period(x)

    dt_from = try_parse(s_from)
    dt_to = try_parse(s_to)
    if dt_from and dt_to and dt_from > dt_to:
        dt_from, dt_to = dt_to, dt_from
    return dt_from, dt_to
```

* 兩次輸入：起始與結束，可留空代表「不限制」。
* 若把起訖反了，會自動**對調**。

---

### 7) 篩選 `filter_df`

```python
def filter_df(df: pd.DataFrame,
              areas: list[str] | None = None,
              dt_from: datetime | None = None,
              dt_to: datetime | None = None) -> pd.DataFrame:
    q = df.copy()
    if areas:
        q = q[q["統計區"].isin(areas)]
    if dt_from is not None:
        q = q[q["period_dt"] >= dt_from]
    if dt_to is not None:
        q = q[q["period_dt"] <= dt_to]
    # 方便閱讀排序
    q = q.sort_values(["統計區", "period_dt"], ascending=[True, True])
    return q
```

* 依 **統計區** 與 **起訖** 條件過濾。
* 最後依 **統計區 → 時間** 排序，輸出更整齊。

---

### 8) 匯出檔案 `export_files`

```python
def export_files(df: pd.DataFrame, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"stat_p_129_{ts}.csv"
    xlsx_path = out_dir / f"stat_p_129_{ts}.xlsx"
    # 輸出
    cols = ["統計期", "統計區", "總處理量", "回收再利用量", "焚化量", "衛生掩埋量", "其他處理量"]
    df[cols].to_csv(csv_path, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df[cols].to_excel(writer, index=False, sheet_name="查詢結果")
    return csv_path, xlsx_path
```

* 確保資料夾存在。
* 產生 **時間戳** 檔名，避免覆蓋。
* **CSV**：只輸出核心欄位，使用 `utf-8-sig`（Excel 開啟不亂碼）。
* **Excel**：用 `openpyxl` 引擎寫入，工作表命名為「查詢結果」。

---

### 9) 主流程 `main()`

```python
def main():
    # 1) 取資料並正規化
    records = load_records(URL)
    df = normalize_df(records)

    # 2) 統計區多選
    area_list = sorted(df["統計區"].dropna().unique().tolist())
    selected_areas = prompt_multi_select(area_list, "統計區")
    if not selected_areas:
        print("未選擇統計區，將不以統計區過濾。")

    # 3) 統計期區間
    dt_from, dt_to = prompt_period_range()

    # 4) 過濾與輸出
    result = filter_df(df, selected_areas, dt_from, dt_to)

    if result.empty:
        print("\n查無資料，請更換條件再試。")
        return

    print(f"\n共 {len(result)} 筆符合。前10筆預覽：")
    preview_cols = ["統計期", "統計區", "總處理量", "回收再利用量", "焚化量", "衛生掩埋量", "其他處理量"]
    print(result[preview_cols].head(10).to_string(index=False))

    csv_path, xlsx_path = export_files(result, OUT_DIR)
    print(f"\n✅ 已輸出：\n- CSV：{csv_path}\n- Excel：{xlsx_path}")
```

* 取 API 資料並整理成乾淨表格。
* 蒐集所有統計區 → 多選互動（沒選就不以統計區過濾）。
* 讓你輸入起訖，套用條件過濾。
* 告訴你總筆數，並印出 **前 10 筆** 便於快速檢查。
* 匯出檔案並顯示路徑。

---

### 10) 入口點與錯誤處理

```python
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n程式發生錯誤：{e}\n請檢查輸入格式或資料欄位。")
```

* 只有直接執行該檔案時才會跑 `main()`（被匯入時不會）。
* 外層接住所有例外，避免程式直接中止；顯示簡明提示。

---

## 常見客製化

* **改輸出位置**：

  ```python
  OUT_DIR = Path(r"D:\exports")
  ```

* **固定查詢（不互動）**：

  ```python
  selected_areas = ["臺北市", "新北市"]
  dt_from = parse_period("112-01")
  dt_to   = parse_period("113-12")
  result = filter_df(df, selected_areas, dt_from, dt_to)
  ```

* **排除只有「年」的紀錄**：

  ```python
  df = df[df["統計期"].str.contains("月", na=False)]
  ```

* **支援「113年度」**：把 `parse_period` 兩處「只有年」的正則從 `年?` 改成 `(年|年度)?`：

  ```python
  # 西元只有年
  m = re.match(r"^(\d{4})(年|年度)?$", s)
  # 民國只有年
  m = re.match(r"^(\d{2,3})(年|年度)?$", s2)
  ```

---

## 小抄（統計期可接受格式）

* **西元**：`2024-07`、`2024/07`、`2024年07月`、`2024`、`2024年`
* **民國**：`113-07`、`113/07`、`113年07月`、`民國113/07`、`113`、`113年`、`民國113年`
* **緊湊**：`YYYYMM`、`YYYMM`

> 只有「年」會視為該年 **1 月**，方便比較與篩選。

---

## 結語

這支腳本把「資料抓取 → 清洗 → 互動式篩選 → 匯出」完整串起來。
若你想改成 **命令列參數**（不互動）、或要 **加總報表**、**輸出同時加上民國/西元標註** 等，我可以直接幫你改版。

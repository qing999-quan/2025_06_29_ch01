#可查詢縣市、統計期並轉出csv及excel檔案到根目錄
import json
import ssl
import urllib.request
from datetime import datetime
import re
import pandas as pd
from pathlib import Path

# ========= 可調參數 =========
URL = ("https://data.moenv.gov.tw/api/v2/stat_p_129"
       "?api_key=58d6040c-dca7-407f-a244-d0bfdfa8144a"
       "&limit=1000&sort=ImportDate%20desc&format=JSON")
OUT_DIR = Path(".")  # 輸出資料夾
# ==========================

context = ssl._create_unverified_context()

def parse_period(s: str) -> datetime:
    """
    解析統計期字串為 datetime（以當月1日或當年1月1日代表）。
    支援：
      - 西元: 2024-07, 2024/07, 2024年07月, 2024, 2024年
      - 民國: 113-07, 113/07, 113年07月, 民國113/07, 113, 113年, 民國113年
    """
    s = s.strip().replace(" ", "")
    # 先嘗試西元：YYYY-MM / YYYY/MM / YYYY年MM月
    for pat in [r"^(\d{4})[-/](\d{1,2})$", r"^(\d{4})年(\d{1,2})月$"]:
        m = re.match(pat, s)
        if m:
            y, mth = int(m.group(1)), int(m.group(2))
            return datetime(y, mth, 1)

    # 西元只有年：YYYY 或 YYYY年 -> 視為該年1月
    m = re.match(r"^(\d{4})年?$", s)
    if m:
        y = int(m.group(1))
        return datetime(y, 1, 1)

    # 民國（先去掉前綴「民國」）
    s2 = re.sub(r"^民國", "", s)
    # 民國年+月：YYY-MM / YYY/MM / YYY年MM月
    for pat in [r"^(\d{2,3})[-/](\d{1,2})$", r"^(\d{2,3})年(\d{1,2})月$"]:
        m = re.match(pat, s2)
        if m:
            roc_y, mth = int(m.group(1)), int(m.group(2))
            y = roc_y + 1911
            return datetime(y, mth, 1)

    # 民國只有年：YYY 或 YYY年 -> 視為該年1月
    m = re.match(r"^(\d{2,3})年?$", s2)
    if m:
        y = int(m.group(1)) + 1911
        return datetime(y, 1, 1)

    # 其他緊湊格式：YYYYMM / YYYMM
    m = re.match(r"^(\d{4})(\d{2})$", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), 1)
    m = re.match(r"^(\d{3})(\d{2})$", s2)
    if m:
        return datetime(int(m.group(1)) + 1911, int(m.group(2)), 1)

    raise ValueError(f"無法解析統計期格式：{s}")


def load_records(url: str) -> list[dict]:
    with urllib.request.urlopen(url, context=context) as resp:
        data = json.loads(resp.read().decode("utf-8-sig"))
    return data["records"]

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

    # 數值轉數字
    for col in ["總處理量", "回收再利用量", "焚化量", "衛生掩埋量", "其他處理量"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n程式發生錯誤：{e}\n請檢查輸入格式或資料欄位。")

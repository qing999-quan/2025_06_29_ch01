# PostgreSQL 匯入與清洗語法教學（Markdown 版）

## 建表（DDL）

```sql
CREATE TABLE IF NOT EXISTS public.執行機關一般廢棄物產生量 (
  統計期 varchar(50) NULL,
  統計區 varchar(50) NULL,
  總產生量 bigint NULL,
  一般垃圾量 bigint NULL,
  資源垃圾量 bigint NULL,
  廚餘量 bigint NULL,
  平均每人每日一般廢棄物產生量 numeric(10,3) NULL
);
```

* `CREATE TABLE IF NOT EXISTS`：表不存在才建立，避免重複報錯。
* `public.`：**Schema**（命名空間）名稱；明確放在 `public`。
* 欄位型別：

  * `varchar(50)`：最多 50 字元的文字。
  * `bigint`（=`int8`）：64 位整數。
  * `numeric(10,3)`：十位有效數字、固定小數三位，適合指標/金額等需要精準小數的欄位。

> **註：** PostgreSQL 的 `float(3)` 不是「小數三位」，實際上會變成二進位浮點（`real`）。若要固定三位小數，請用 `numeric(10,3)`。

---

## 清洗 + 插入（ETL）

```sql
INSERT INTO public.執行機關一般廢棄物產生量 (
  統計期, 統計區, 總產生量, 一般垃圾量, 資源垃圾量, 廚餘量, 平均每人每日一般廢棄物產生量
)
SELECT
  NULLIF(btrim(統計期), ''),
  NULLIF(btrim(統計區), ''),

  NULLIF(regexp_replace(總產生量,   '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(一般垃圾量, '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(資源垃圾量, '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(廚餘量,     '[^0-9\-]', '', 'g'), '')::bigint,

  CASE
    WHEN NULLIF(btrim(平均每人每日一般廢棄物產生量), '') IS NULL THEN NULL
    ELSE NULLIF(
           regexp_replace(
             replace(btrim(平均每人每日一般廢棄物產生量), ',', '.'),
             '[^0-9\.\-]', '', 'g'
           ),
           ''
         )::numeric(10,3)
  END
FROM 執行機關一般廢棄物產生量_raw;
```

**語法重點：**

* `INSERT ... SELECT ... FROM _raw`：從原始表一次清洗匯入正式表。
* `btrim(欄位)`：去左右端空白（含全形空白可再擴充）。
* `NULLIF(expr, '')`：把空字串轉成 `NULL`。
* `regexp_replace(col, '[^0-9\-]', '', 'g')`：**只保留數字與負號**，移除千分位逗號、全形空白、單位字、不可見字元等。
* `replace(val, ',', '.')`：將歐陸小數逗號改成 `.`。
* `::bigint` / `::numeric(10,3)`：字串清洗後再**型別轉換**，避免「Can't parse numeric value」。

---

## 為什麼要這樣設計？

* **\_raw 全字串 → SQL 清洗 → 正式表**：最穩健，匯入不會因格式髒而中斷。
* **`NULLIF + btrim`**：把看似空值的內容（`''`、`'  '`）正確轉為 `NULL`。
* **`regexp_replace`**：保守清洗，面對不同來源的 CSV 也不怕。
* **`numeric(10,3)`**：固定小數三位、可控的四捨五入與比較行為。

---

## 清洗前後對照

| 來源字串            | 清洗步驟摘要                                  | 目標型別    | 結果        |
| --------------- | --------------------------------------- | ------- | --------- |
| `' 1,051,951 '` | `regexp_replace(..., '[^0-9\-]', '')`   | bigint  | `1051951` |
| `'1 051 951'`   | 同上                                      | bigint  | `1051951` |
| `''` / `'   '`  | `NULLIF(btrim(...), '')`                | 任意      | `NULL`    |
| `' 0,873 '`     | `replace(',', '.')` → `::numeric(10,3)` | numeric | `0.873`   |

---

## Schema 與命名小抄

```sql
-- 建立常設表（出現在物件樹）
CREATE TABLE public."執行機關一般廢棄物產生量" (...);

-- 讀常設表（明確指定 schema）
SELECT * FROM public."執行機關一般廢棄物產生量";

-- 建暫存表（只在本連線；位於 pg_temp，不在 public）
CREATE TEMP TABLE "執行機關一般廢棄物產生量_raw" (...);

-- 讀暫存表（同一連線可直接使用）
SELECT * FROM "執行機關一般廢棄物產生量_raw";
```

* 中文/含特殊字元的表名請用**雙引號**。
* 查表在哪個 schema：

  ```sql
  SELECT table_schema, table_name
  FROM information_schema.tables
  WHERE table_name LIKE '執行機關一般廢棄物產生量%';
  ```
* 查看搜尋路徑（`search_path`）：

  ```sql
  SHOW search_path;
  ```

---

## 進一步建議（可選）

**索引：** 常查「期間 + 區域」可加複合索引

```sql
CREATE INDEX ON public.執行機關一般廢棄物產生量 (統計期, 統計區);
```

**檢核：** 避免負值

```sql
ALTER TABLE public.執行機關一般廢棄物產生量
  ADD CONSTRAINT chk_nonnegative
  CHECK (
    COALESCE(總產生量,0) >= 0 AND
    COALESCE(一般垃圾量,0) >= 0 AND
    COALESCE(資源垃圾量,0) >= 0 AND
    COALESCE(廚餘量,0) >= 0 AND
    COALESCE(平均每人每日一般廢棄物產生量,0) >= 0
  );
```

---

## 一鍵流程（示意）

```sql
-- 1) 建常設 raw（只需一次）
CREATE TABLE IF NOT EXISTS public."執行機關一般廢棄物產生量_raw"(
  統計期 text, 統計區 text, 總產生量 text, 一般垃圾量 text,
  資源垃圾量 text, 廚餘量 text, 平均每人每日一般廢棄物產生量 text
);

-- 2) 每次匯入前清空 raw
TRUNCATE public."執行機關一般廢棄物產生量_raw";

-- 3) 匯入 CSV（pgAdmin Import 或 psql 的 \copy）

-- 4) 清洗 → 寫入正式表
INSERT INTO public."執行機關一般廢棄物產生量"(統計期, 統計區, 總產生量, 一般垃圾量, 資源垃圾量, 廚餘量, 平均每人每日一般廢棄物產生量)
SELECT
  NULLIF(btrim(統計期), ''),
  NULLIF(btrim(統計區), ''),
  NULLIF(regexp_replace(總產生量,   '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(一般垃圾量, '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(資源垃圾量, '[^0-9\-]', '', 'g'), '')::bigint,
  NULLIF(regexp_replace(廚餘量,     '[^0-9\-]', '', 'g'), '')::bigint,
  CASE
    WHEN NULLIF(btrim(平均每人每日一般廢棄物產生量), '') IS NULL THEN NULL
    ELSE NULLIF(
           regexp_replace(
             replace(btrim(平均每人每日一般廢棄物產生量), ',', '.'),
             '[^0-9\.\-]', '', 'g'
           ),
           ''
         )::numeric(10,3)
  END;
```

---

需要我把這份 Markdown 另存成檔（.md）給你下載嗎？或是要加上你實際的表名/檔名範例再客製一次？

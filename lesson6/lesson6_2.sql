ALTER TABLE "114年定檢項目及金額" ADD PRIMARY KEY ("項目");

ALTER TABLE "114年定檢項目地點及次數" ADD FOREIGN KEY ("項目")
REFERENCES "114年定檢項目及金額"("項目");

SELECT
  p.項目,
  SUM(
    (COALESCE(d.第1季,0)
    + COALESCE(d.第2季,0)
    + COALESCE(d."第3季-1",0)
    + COALESCE(d."第3季-2",0)
    + COALESCE(d."第4季-1",0)
    + COALESCE(d."第4季-2",0)) * p.單價
  ) AS 總金額
FROM
  public."114年定檢項目及金額" p
JOIN
  public."114年定檢項目地點及次數" d
ON p.項目 = d.項目
GROUP BY p.項目;

SELECT
  p.項目,
  SUM(COALESCE(d.第1季,0)) AS 第1季次數,
  SUM(COALESCE(d.第2季,0)) AS 第2季次數,
  SUM(COALESCE(d."第3季-1",0)) AS 第3_1季次數,
  SUM(COALESCE(d."第3季-2",0)) AS 第3_2季次數,
  SUM(COALESCE(d."第4季-1",0)) AS 第4_1季次數,
  SUM(COALESCE(d."第4季-2",0)) AS 第4_2季次數,
  SUM(( COALESCE(d.第1季,0)
      + COALESCE(d.第2季,0)
      + COALESCE(d."第3季-1",0)
      + COALESCE(d."第3季-2",0)
      + COALESCE(d."第4季-1",0)
      + COALESCE(d."第4季-2",0)) * p.單價) AS 總金額
FROM
  public."114年定檢項目及金額" p
JOIN
  public."114年定檢項目地點及次數" d
ON p.項目 = d.項目
GROUP BY p.項目;

SELECT
  p.項目,
  SUM(
    (COALESCE(d.第1季,0)
    + COALESCE(d.第2季,0)
    + COALESCE(d."第3季-1",0)
    + COALESCE(d."第3季-2",0)
    + COALESCE(d."第4季-1",0)
    + COALESCE(d."第4季-2",0))
  ) AS 總次數
FROM
  public."114年定檢項目及金額" p
JOIN
  public."114年定檢項目地點及次數" d
ON p.項目 = d.項目
GROUP BY p.項目;

SELECT
  a.項目,
  a.項次,
  a.單價,
  d.地點,
  d.第1季,
  d.第2季,
  d."第3季-1",
  d."第3季-2",
  d."第4季-1",
  d."第4季-2"
FROM public."114年定檢項目及金額" a
LEFT JOIN public."114年定檢項目地點及次數" d
ON a.項目 = d.項目
WHERE d.地點 LIKE '%放流口%';

SELECT
  a.項目,
  a.單價,
  d.地點,
  d.第1季,
  d.第2季,
  d."第3季-1",
  d."第3季-2",
  d."第4季-1",
  d."第4季-2"
FROM public."114年定檢項目及金額" a
JOIN public."114年定檢項目地點及次數" d
ON a.項目 = d.項目;

SELECT
  a.項目,
  a.項次,
  a.單價,
  d.地點,
  d.第1季,
  d.第2季,
  d."第3季-1",
  d."第3季-2",
  d."第4季-1",
  d."第4季-2",
  -- 將所有季次欄位加總，空值用0代替
  (
    COALESCE(d.第1季, 0)
    + COALESCE(d.第2季, 0)
    + COALESCE(d."第3季-1", 0)
    + COALESCE(d."第3季-2", 0)
    + COALESCE(d."第4季-1", 0)
    + COALESCE(d."第4季-2", 0)
  ) AS 總次數,
  -- 總次數乘上單價算總金額
  (
    (
      COALESCE(d.第1季, 0)
      + COALESCE(d.第2季, 0)
      + COALESCE(d."第3季-1", 0)
      + COALESCE(d."第3季-2", 0)
      + COALESCE(d."第4季-1", 0)
      + COALESCE(d."第4季-2", 0)
    ) * a.單價
  ) AS 總金額
FROM public."114年定檢項目及金額" a
LEFT JOIN public."114年定檢項目地點及次數" d
ON a.項目 = d.項目;
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
  SUM(
    (
      COALESCE(d.第1季,0)
      + COALESCE(d.第2季,0)
      + COALESCE(d."第3季-1",0)
      + COALESCE(d."第3季-2",0)
      + COALESCE(d."第4季-1",0)
      + COALESCE(d."第4季-2",0)
    ) * p.單價
  ) AS 總金額
FROM
  public."114年定檢項目及金額" p
JOIN
  public."114年定檢項目地點及次數" d
ON p.項目 = d.項目
GROUP BY p.項目;
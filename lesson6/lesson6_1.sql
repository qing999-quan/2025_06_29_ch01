ALTER TABLE "台鐵車站資訊" ADD PRIMARY KEY ("stationCode");


ALTER TABLE "每日各站進出站人數" ADD FOREIGN KEY ("車站代碼")
REFERENCES "台鐵車站資訊"("stationCode");

SELECT count(*) AS "總筆數"
FROM "每日各站進出站人數";


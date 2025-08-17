SELECT t."stationName" AS "車站名稱",
	p."日期",
	p."進站人數",
	p."出站人數"
FROM "每日各站進出站人數" p
LEFT JOIN "台鐵車站資訊" t ON p."車站代碼" = t."stationCode"
WHERE t."stationName" = '基隆' AND p."日期" = '2023-01-01';
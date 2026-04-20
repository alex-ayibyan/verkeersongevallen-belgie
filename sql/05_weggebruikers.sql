-- Business vraag 5: Welke weggebruikers zijn het meest betrokken?

-- Meest betrokken weggebruikers (partij 1)
SELECT "TX_ROAD_USR_TYPE1_NL" AS weggebruiker, COUNT(*) AS aantal
FROM ongevallen
WHERE "TX_ROAD_USR_TYPE1_NL" IS NOT NULL
GROUP BY "TX_ROAD_USR_TYPE1_NL"
ORDER BY aantal DESC;

-- Meest voorkomende combinaties van betrokken partijen
SELECT "TX_ROAD_USR_TYPE1_NL" AS partij_1,
       "TX_ROAD_USR_TYPE2_NL" AS partij_2,
       COUNT(*) AS aantal
FROM ongevallen
WHERE "TX_ROAD_USR_TYPE1_NL" IS NOT NULL
  AND "TX_ROAD_USR_TYPE2_NL" IS NOT NULL
GROUP BY partij_1, partij_2
ORDER BY aantal DESC
LIMIT 15;

-- Weggebruikers bij dodelijke ongevallen
SELECT "TX_ROAD_USR_TYPE1_NL" AS weggebruiker,
       COUNT(*) AS dodelijke_ongevallen
FROM ongevallen
WHERE ernst ILIKE '%dode%'
  AND "TX_ROAD_USR_TYPE1_NL" IS NOT NULL
GROUP BY weggebruiker
ORDER BY dodelijke_ongevallen DESC;

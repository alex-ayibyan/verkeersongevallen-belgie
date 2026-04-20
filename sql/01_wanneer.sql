-- Business vraag 1: Wanneer gebeuren de meeste ongevallen?

-- Per jaar
SELECT jaar, COUNT(*) AS aantal
FROM ongevallen
GROUP BY jaar
ORDER BY jaar;

-- Per maand
SELECT maand, maand_naam, COUNT(*) AS aantal
FROM ongevallen
GROUP BY maand, maand_naam
ORDER BY maand;

-- Per uur van de dag
SELECT hour AS uur, COUNT(*) AS aantal
FROM ongevallen
GROUP BY hour
ORDER BY hour;

-- Piekuur per jaar
SELECT jaar, hour AS piekuur, COUNT(*) AS aantal
FROM ongevallen
GROUP BY jaar, hour
ORDER BY jaar, aantal DESC;

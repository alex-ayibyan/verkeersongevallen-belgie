-- Business vraag 3: Hoe evolueert het aantal ongevallen over de jaren?

-- Totaal per jaar
SELECT jaar, COUNT(*) AS aantal,
       ROUND(100.0 * (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY jaar))
             / NULLIF(LAG(COUNT(*)) OVER (ORDER BY jaar), 0), 1) AS pct_verandering
FROM ongevallen
GROUP BY jaar
ORDER BY jaar;

-- Ernst per jaar
SELECT jaar, ernst, COUNT(*) AS aantal
FROM ongevallen
GROUP BY jaar, ernst
ORDER BY jaar, aantal DESC;

-- Aandeel dodelijke ongevallen per jaar (%)
SELECT jaar,
       COUNT(*) AS totaal,
       SUM(CASE WHEN ernst ILIKE '%dode%' THEN 1 ELSE 0 END) AS dodelijk,
       ROUND(100.0 * SUM(CASE WHEN ernst ILIKE '%dode%' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_dodelijk
FROM ongevallen
GROUP BY jaar
ORDER BY jaar;

-- ============================================================
-- Verkeersongevallen België — SQL Analyse
-- ============================================================

-- 1. Totaal aantal ongevallen per jaar
SELECT
    jaar,
    COUNT(*)                                          AS aantal_ongevallen,
    COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY jaar)    AS verschil_vorig_jaar,
    ROUND(
        100.0 * (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY jaar))
        / NULLIF(LAG(COUNT(*)) OVER (ORDER BY jaar), 0), 1
    )                                                 AS pct_verandering
FROM ongevallen
GROUP BY jaar
ORDER BY jaar;


-- 2. Top 10 gevaarlijkste gemeentes
SELECT
    gemeente,
    provincie,
    COUNT(*)  AS aantal_ongevallen
FROM ongevallen
GROUP BY gemeente, provincie
ORDER BY aantal_ongevallen DESC
LIMIT 10;


-- 3. Ongevallen per uur van de dag (piekuren)
SELECT
    uur,
    COUNT(*)                                   AS aantal,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_van_totaal
FROM ongevallen
GROUP BY uur
ORDER BY uur;


-- 4. Verdeling per ernst (doden, zwaargewonden, lichtgewonden)
SELECT
    ernst,
    COUNT(*)  AS aantal,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM ongevallen
GROUP BY ernst
ORDER BY aantal DESC;


-- 5. Gevaarlijkste combinatie: dag + uur
SELECT
    dag_van_week,
    uur,
    COUNT(*) AS aantal
FROM ongevallen
GROUP BY dag_van_week, uur
ORDER BY aantal DESC
LIMIT 20;


-- 6. Evolutie per provincie over de jaren (voor Power BI trendlijn)
SELECT
    jaar,
    provincie,
    COUNT(*) AS aantal
FROM ongevallen
GROUP BY jaar, provincie
ORDER BY jaar, provincie;


-- 7. Aandeel dodelijke ongevallen per provincie
SELECT
    provincie,
    COUNT(*)                                             AS totaal,
    SUM(CASE WHEN ernst = 'dood' THEN 1 ELSE 0 END)     AS dodelijk,
    ROUND(
        100.0 * SUM(CASE WHEN ernst = 'dood' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                    AS pct_dodelijk
FROM ongevallen
GROUP BY provincie
ORDER BY pct_dodelijk DESC;


-- 8. Seizoenspatroon: maand vergelijking
SELECT
    maand,
    TO_CHAR(TO_DATE(maand::text, 'MM'), 'Month') AS maand_naam,
    COUNT(*)                                      AS aantal
FROM ongevallen
GROUP BY maand
ORDER BY maand;

-- Business vraag 2: Welke provincies en gemeentes zijn het gevaarlijkst?

-- Per provincie
SELECT provincie, COUNT(*) AS aantal
FROM ongevallen
WHERE provincie != 'Onbekend'
GROUP BY provincie
ORDER BY aantal DESC;

-- Top 20 gevaarlijkste gemeentes
SELECT gemeente, provincie, COUNT(*) AS aantal
FROM ongevallen
WHERE gemeente IS NOT NULL
GROUP BY gemeente, provincie
ORDER BY aantal DESC
LIMIT 20;

-- Provincie met meeste dodelijke ongevallen
SELECT provincie, COUNT(*) AS dodelijke_ongevallen
FROM ongevallen
WHERE ernst ILIKE '%dode%'
  AND provincie != 'Onbekend'
GROUP BY provincie
ORDER BY dodelijke_ongevallen DESC;

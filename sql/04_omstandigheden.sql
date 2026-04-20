-- Business vraag 4: Meest voorkomende oorzaken en wegtypen?

-- Per wegtype
SELECT wegtype, COUNT(*) AS aantal
FROM ongevallen
WHERE wegtype IS NOT NULL
GROUP BY wegtype
ORDER BY aantal DESC;

-- Per weersomstandigheid
SELECT weer, COUNT(*) AS aantal
FROM ongevallen
WHERE weer IS NOT NULL
GROUP BY weer
ORDER BY aantal DESC;

-- Per lichtomstandigheid
SELECT licht, COUNT(*) AS aantal
FROM ongevallen
WHERE licht IS NOT NULL
GROUP BY licht
ORDER BY aantal DESC;

-- Combinatie wegtype + ernst
SELECT wegtype, ernst, COUNT(*) AS aantal
FROM ongevallen
WHERE wegtype IS NOT NULL AND ernst IS NOT NULL
GROUP BY wegtype, ernst
ORDER BY wegtype, aantal DESC;

-- @block populate team table with data from 'riders' table
INSERT INTO teams (team, manufacturer, gp_class)
SELECT DISTINCT team,
    MAX(bike),
    MAX(gp_class)
FROM riders
WHERE team IS NOT NULL
GROUP BY team
ORDER BY team ASC;
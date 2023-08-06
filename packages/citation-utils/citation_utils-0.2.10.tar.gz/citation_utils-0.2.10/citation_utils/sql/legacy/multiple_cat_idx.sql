SELECT
    COUNT(docket_date) num,
    docket_category,
    docket_serial,
    MIN(docket_date) earliest,
    MAX(docket_date) latest,
    MAX(docket_date) - MIN(docket_date) diff,
    -- large difference is indicative of impropriety in at least one category / serial pair
    json_group_array(docket_date) dates,
    json_group_array(origin) origins,
    json_group_array(title) titles
FROM
    valid
WHERE
    docket_date IS NOT NULL
GROUP BY
    docket_category,
    docket_serial
HAVING
    num >= 2
ORDER BY
    diff DESC,
    num DESC

DELETE FROM net_samples
WHERE
    rowid NOT IN (
        SELECT
            rowid
        FROM
            net_samples
        ORDER BY
            timestamp DESC
        LIMIT
            ?
    )
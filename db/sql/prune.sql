DELETE FROM net_samples
WHERE
    device_name = ?
    AND rowid NOT IN (
        SELECT
            rowid
        FROM
            net_samples
        ORDER BY
            timestamp DESC
        LIMIT
            ?
    )
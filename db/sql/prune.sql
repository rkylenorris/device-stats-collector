DELETE FROM net_samples
WHERE
    device_name = ?
    AND rowid NOT IN (
        SELECT
            rowid
        FROM
            net_samples
        WHERE
            device_name = ?
        ORDER BY
            timestamp DESC
        LIMIT
            ?
    )
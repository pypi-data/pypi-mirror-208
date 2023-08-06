SELECT_POSITIONS_FOR_ENVIRONMENT = """
WITH
    coordinate_spaces AS (
        SELECT * FROM spaces WHERE type_name = 'CoordinateSpace'
    ),
    uwb_devices AS (
        SELECT * FROM devices WHERE data->>'device_type' = 'UWBTAG'
    )
SELECT
    e.environment_id AS environment_id,
    e.data->>'name' AS environment_name,
    c.space_id AS coordinate_space_id,
    d.device_id AS device_id,
    d.data->>'name' AS device_name,
    d.data->>'serial_number' AS device_serial_number,
    persons_detailed.person_id AS person_id,
    persons_detailed.person_name AS person_name,
    tray_materials_detailed.tray_id AS tray_id,
    tray_materials_detailed.tray_name AS tray_name,
    tray_materials_detailed.material_id AS material_id,
    tray_materials_detailed.material_name AS material_name,
    positions.position_id AS position_id,
    to_timestamp(positions.data->>'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS position_timestamp,
    positions.data->'coordinates' AS position_coordinates,
    positions.data->'anchor_count' AS position_anchor_count,
    positions.data->'quality' AS position_quality
FROM
    environments e
    INNER JOIN coordinate_spaces c
        ON e.environment_id::text = c.data->>'environment'
    INNER JOIN positions
        ON positions.coordinate_space = c.space_id 
    INNER JOIN uwb_devices d
        ON d.device_id = positions.object
    LEFT JOIN
        (
            SELECT
                persons.person_id AS person_id,
                persons.data->>'name' AS person_name,
                ea.data->>'device' AS device_id,
                ea.data->>'entity_type' AS entity_type
            FROM entityassignments ea 
            INNER JOIN persons
            ON persons.person_id::text = ea.data->>'entity'
            WHERE
                to_timestamp(ea.data->>'start', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') <= %(classroom_end_time)s AND
                (
                    ea.data->>'end' is NULL OR
                    to_timestamp(ea.data->>'end', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') >= %(classroom_start_time)s
                )
        ) persons_detailed
        ON d.device_id::text = persons_detailed.device_id
    LEFT JOIN
        (
            SELECT
                m.material_id AS material_id,
                m.data->>'name' AS material_name,
                t.tray_id::text AS tray_id,
                t.data->>'name' AS tray_name,
                ea.data->>'device' AS device_id,
                ea.data->>'entity_type' AS entity_type
            FROM materialassignments ma
            INNER JOIN material m
                ON m.material_id::text = ma.data->>'material'
            INNER JOIN entityassignments ea 
                ON ma.data->>'tray' = ea.data->>'entity'
            INNER JOIN trays t
                ON t.tray_id::text = ma.data->>'tray'
            WHERE
                to_timestamp(ea.data->>'start', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') <= %(classroom_end_time)s AND
                (
                    ea.data->>'end' is NUll OR
                    to_timestamp(ea.data->>'end', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') >= %(classroom_start_time)s
                )
        ) tray_materials_detailed
        ON d.device_id::text = tray_materials_detailed.device_id
WHERE
    e.data->>'name' = %(environment_name)s AND
    positions.timestamp >= %(classroom_start_time)s AND
    positions.timestamp <= %(classroom_end_time)s
"""

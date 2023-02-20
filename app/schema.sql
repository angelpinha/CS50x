SELECT id, 
    name,
    stored_quantity,
    unit 
FROM 
    items
INNER JOIN inventory
    ON items.id = inventory.item_id
WHERE item_id = ?;
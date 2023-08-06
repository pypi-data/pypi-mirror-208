CREATE TRIGGER IF NOT EXISTS update_membership_id after
INSERT
    ON {{ membership_tbl }}
BEGIN
UPDATE
    {{ membership_tbl }}
    -- the individual id is not yet populated in the details.yaml prompting need for trigger
    set individual_id = (
        SELECT
            x.id
        FROM
            {{ individual_tbl }}
            x
        WHERE
            x.email = account_email
    );
END;

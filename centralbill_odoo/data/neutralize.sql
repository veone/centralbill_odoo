-- disable centralbill payment provider
UPDATE payment_provider
   SET centralbill_app_key = NULL,
       centralbill_app_name = NULL,
       centralbill_secret_key = NULL;
## do a migration with alembic

`alembic revision --autogenerate -m "Initial migration"`

## to push the migration to the DB:

`alembic upgrade head`

## Generate private key (P-384 curve)

`openssl ecparam -name secp384r1 -genkey -noout -out private.pem`

## Generate public key from private key

`openssl ec -in private.pem -pubout -out public.pem`
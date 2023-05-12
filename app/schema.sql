CREATE TABLE "users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"username"	TEXT NOT NULL UNIQUE,
	"password_hash"	BLOB NOT NULL,
	"uuid" TEXT NOT NULL,
	"totp_key" TEXT,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"role"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "customers" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"acquisition_date"	TEXT NOT NULL,
	"email"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "suppliers" (
	"id"	INTEGER NOT NULL UNIQUE,
	"supplier_name"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "products" (
	"id"	INTEGER NOT NULL UNIQUE,
	"description"	TEXT NOT NULL,
	"sell_value"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "items" (
	"id"	INTEGER NOT NULL UNIQUE,
	"product_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"department"	TEXT NOT NULL,
	"format"	INTEGER NOT NULL,
	"unit"	TEXT NOT NULL,
	"purchase_value"	INTEGER NOT NULL,
	FOREIGN KEY("product_id") REFERENCES "products"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "inventory" (
	"item_id"	INTEGER,
	"initial_quantity"	INTEGER NOT NULL,
	"stored_quantity"	INTEGER NOT NULL,
	FOREIGN KEY("item_id") REFERENCES "items"("id")
);

CREATE TABLE "purchases" (
	"item_id"	INTEGER,
	"supplier_id"	INTEGER,
	"invoice_number"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"quantity"	INTEGER NOT NULL,
	FOREIGN KEY("supplier_id") REFERENCES "suppliers"("id"),
	FOREIGN KEY("item_id") REFERENCES "items"("id")
);

CREATE TABLE "sales" (
	"seller_id"	INTEGER,
	"product_id"	INTEGER,
	"customer_id"	INTEGER,
	"transaction_number"	INTEGER NOT NULL UNIQUE,
	"quantity"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("transaction_number" AUTOINCREMENT),
	FOREIGN KEY("product_id") REFERENCES "products"("id"),
	FOREIGN KEY("seller_id") REFERENCES "users"("id"),
	FOREIGN KEY("customer_id") REFERENCES "customers"("id")
);

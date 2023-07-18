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
	"price"	REAL NOT NULL CHECK("price" == round("price", 2)),
	"category" TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "categories" (
	"id" INTEGER NOT NULL UNIQUE,
	"product_category" TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "items" (
	"id"	INTEGER NOT NULL UNIQUE,
	"product_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"cost_center"	TEXT NOT NULL,
	"format"	INTEGER NOT NULL,
	"unit"	TEXT NOT NULL,
	"updated_price"	REAL NOT NULL CHECK("updated_price" == round("updated_price", 2)),
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
	"purchase_price" REAL NOT NULL CHECK("purchase_price" == round("purchase_price", 2)),
	FOREIGN KEY("supplier_id") REFERENCES "suppliers"("id"),
	FOREIGN KEY("item_id") REFERENCES "items"("id")
);

CREATE TABLE "sales" (
	"id"	INTEGER NOT NULL UNIQUE,
	"transaction_number" INTEGER NOT NULL,
	"product_id"	INTEGER,
	"quantity"	INTEGER NOT NULL,
	"amount"	REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("product_id") REFERENCES "products"("id")
);

CREATE TABLE "balance" (
	"id" INTEGER NOT NULL UNIQUE,
	"revenues" REAL NOT NULL,
	"expenses" REAL NOT NULL,
	"income" REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO balance (revenues, expenses, income) VALUES (5000, 0, 5000);

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "themes_name" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "events" (
	"id"	INTEGER,
	"title"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"date_time"	TEXT NOT NULL,
	"theme_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("theme_id") REFERENCES "themes_name"("id")
);
INSERT INTO "themes_name" VALUES (1,'Football');
INSERT INTO "themes_name" VALUES (2,'Programing');
INSERT INTO "themes_name" VALUES (4,'Films');
INSERT INTO "events" VALUES (1,'Champion Leque','Lets watch whit us','2023-09-31 12:30:00',1);
INSERT INTO "events" VALUES (2,'Phython ','Ми гавчимося базовим наичкам за лічені години','2023-09-31 12:30:00',2);
INSERT INTO "events" VALUES (3,'Avatar','Lets watch together','2023-08-31 12:30:00',4);
COMMIT;

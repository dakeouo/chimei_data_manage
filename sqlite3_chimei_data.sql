BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "model_group" (
	"group_id"	varchar(50) NOT NULL UNIQUE,
	"model"	varchar(30) NOT NULL,
	"groups"	varchar(40) NOT NULL,
	PRIMARY KEY("group_id")
);
INSERT INTO "model_group" ("group_id","model","groups") VALUES ('tbi_training','TBI','training'),
 ('tbi_pre','TBI','Sham'),
 ('tbi_sham_ns','TBI','Sham+NS'),
 ('tbi_sham_msc','TBI','Sham+MSC'),
 ('tbi_rtbi_ns','TBI','rTBI+NS'),
 ('tbi_rtbi_msc','TBI','rTBI+MSC');
CREATE TABLE IF NOT EXISTS "exp_timepoint" (
	"tp_no"	varchar(10) NOT NULL UNIQUE,
	"tp_show"	varchar(10) NOT NULL,
	"note"	varchar(64) DEFAULT NULL,
	PRIMARY KEY("tp_no")
);
INSERT INTO "exp_timepoint" ("tp_no","tp_show","note") VALUES ('00M07D','D07','手術後7天'),
 ('00M14D','D14','手術後14天'),
 ('00M28D','D28','手術後28天'),
 ('03M00D','M03','手術後3個月'),
 ('06M00D','M06','手術後6個月'),
 ('09M00D','M09','手術後9個月'),
 ('pre','Pre','手術前行為測試'),
 ('training','Training','訓練期');
CREATE TABLE IF NOT EXISTS "exp_detail" (
	"serial_data_id"	varchar(50) NOT NULL UNIQUE,
	"exp_date_id"	varchar(30) NOT NULL,
	"groups"	varchar(50) NOT NULL,
	"rat_id"	smallint(5) NOT NULL,
	"short_term"	smallint(5) NOT NULL,
	"long_term"	smallint(5) NOT NULL,
	"latency"	int(10) NOT NULL,
	"DisC"	varchar(10) DEFAULT 0,
	"DisT"	varchar(10) DEFAULT 0,
	"DisN"	varchar(10) DEFAULT 0,
	"TimeC"	varchar(10) DEFAULT 0,
	"TimeT"	varchar(10) DEFAULT 0,
	"TimeN"	varchar(10) DEFAULT 0,
	"isFilter"	tinyint(1) DEFAULT 1,
	PRIMARY KEY("serial_data_id"),
	FOREIGN KEY("groups") REFERENCES "model_group"("group_id"),
	FOREIGN KEY("exp_date_id") REFERENCES "exp_date"("ExpNo")
);
CREATE TABLE IF NOT EXISTS "exp_route" (
	"serial_data_id"	varchar(50) NOT NULL,
	"route_no"	smallint(5) NOT NULL,
	"arm_no"	tinyint(2) NOT NULL,
	FOREIGN KEY("serial_data_id") REFERENCES "exp_detail"("serial_data_id")
);
CREATE TABLE IF NOT EXISTS "exp_date" (
	"ExpNo"	varchar(30) NOT NULL UNIQUE,
	"ExpDate"	date NOT NULL,
	"Model"	varchar(30) NOT NULL,
	"Timepoint"	varchar(10) NOT NULL,
	"CSV_Upload"	tinyint(1) DEFAULT 0,
	"IMG_Upload"	tinyint(1) DEFAULT 0,
	"PathState"	tinyint(2) NOT NULL,
	PRIMARY KEY("ExpNo"),
	FOREIGN KEY("Timepoint") REFERENCES "exp_timepoint"("tp_no")
);
CREATE VIEW "VIEW_TOTAL_Export_Rowdata" AS
SELECT "exp_detail"."serial_data_id" AS "RatSerialID", 
"model_group"."model" AS "Models", "model_group"."groups" AS "Groups", "exp_timepoint"."tp_show" AS "Timepoint",
"exp_detail"."short_term" AS "ShortTerm", "exp_detail"."long_term" AS "LongTerm", "exp_detail"."latency" AS "Latency", 
"exp_detail"."DisC" AS "Distance(Central)", "exp_detail"."DisT" AS "Distance(Target)", "exp_detail"."DisN" AS "Distance(Normal)",
"exp_detail"."TimeC" AS "Time(Central)", "exp_detail"."TimeT" AS "Time(Target)", "exp_detail"."TimeN" AS "Time(Normal)",
count(CASE WHEN "exp_route"."arm_no" IN(2, 4, 6, 8) THEN 1 END) AS "Arm(Target)",
count(CASE WHEN "exp_route"."arm_no" IN(1, 3, 5, 7) THEN 1 END) AS "Arm(Normal)",
count("exp_route"."arm_no")-1 AS "Arm(Central)"
FROM "exp_detail" 
LEFT JOIN "model_group" ON "exp_detail"."groups" = "model_group"."group_id"
LEFT JOIN "exp_date" ON "exp_detail"."exp_date_id" = "exp_date"."ExpNo"
LEFT JOIN "exp_timepoint" ON "exp_timepoint"."tp_no" = "exp_date"."Timepoint"
LEFT JOIN "exp_route" ON "exp_route"."serial_data_id" = "exp_detail"."serial_data_id"
WHERE "exp_detail"."isFilter" = 1 GROUP BY "exp_detail"."serial_data_id";
CREATE VIEW "VIEW_TOTAL_Experiment_Overview" AS
SELECT "exp_date"."ExpNo", "exp_date"."ExpDate", "exp_date"."Model" AS "Models", "exp_date"."Timepoint", "exp_date"."PathState",
"exp_date"."CSV_Upload", "exp_date"."IMG_Upload",
count(CASE WHEN "exp_detail"."groups" = "tbi_pre" THEN 1 END) AS "group(pre)",
count(CASE WHEN "exp_detail"."groups" = "tbi_sham_ns" THEN 1 END) AS "group(Sham+NS)",
count(CASE WHEN "exp_detail"."groups" = "tbi_sham_msc" THEN 1 END) AS "group(Sham+MSC)",
count(CASE WHEN "exp_detail"."groups" = "tbi_rtbi_ns" THEN 1 END) AS "group(rTBI+NS)",
count(CASE WHEN "exp_detail"."groups" = "tbi_rtbi_msc" THEN 1 END) AS "group(rTBI+MSC)",
count("exp_detail"."groups") AS "Total"
FROM "exp_date" LEFT JOIN "exp_detail" ON "exp_date"."ExpNo" = "exp_detail"."exp_date_id" 
WHERE "exp_detail"."groups" <> "tbi_training" GROUP BY "ExpNo";
CREATE VIEW "VIEW_TOTAL_ExpDetail_Data" AS
SELECT "exp_route"."serial_data_id", "model_group"."model" AS "Models", "exp_date"."ExpDate", "model_group"."groups", "exp_timepoint"."tp_show" AS "timepoints",
"exp_detail"."rat_id", "exp_detail"."long_term", "exp_detail"."short_term",
round((CAST("exp_detail"."TimeC" AS float)/ CAST("exp_detail"."latency" AS float)),2) AS "Speed(Central)",
round((CAST("exp_detail"."TimeT" AS float)/ CAST("exp_detail"."latency" AS float)),2) AS "Speed(Target)",
round((CAST("exp_detail"."TimeN" AS float)/ CAST("exp_detail"."latency" AS float)),2) AS "Speed(Normal)",
round((CAST("exp_detail"."DisC" AS float)+CAST("exp_detail"."DisT" AS float)+CAST("exp_detail"."DisN" AS float))/(CAST("exp_detail"."TimeC" AS float)+CAST("exp_detail"."TimeT" AS float)+CAST("exp_detail"."TimeN" AS float)),1) AS "Speed(Total)",
round((CAST("exp_detail"."DisC" AS float)+CAST("exp_detail"."DisT" AS float)+CAST("exp_detail"."DisN" AS float)),1) AS "distance",
"exp_detail"."latency", "exp_detail"."isFilter"
FROM "exp_detail" LEFT JOIN "model_group" ON "exp_detail"."groups" = "model_group"."group_id"
LEFT JOIN "exp_date" ON "exp_detail"."exp_date_id" = "exp_date"."ExpNo"
LEFT JOIN "exp_route" ON "exp_detail"."serial_data_id" = "exp_route"."serial_data_id"
LEFT JOIN "exp_timepoint" ON "exp_timepoint"."tp_no" = "exp_date"."Timepoint"
WHERE "model_group"."groups" <> "training" GROUP BY "exp_detail"."serial_data_id" ORDER BY "exp_detail"."serial_data_id", "model_group"."groups", "exp_detail"."rat_id";
COMMIT;

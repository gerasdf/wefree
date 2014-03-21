sqlite3 webdb.sqlite3 << EOF
CREATE TABLE "ap" (
    "bssid" varchar(25) NOT NULL PRIMARY KEY,
    "essid" varchar(128) NOT NULL,
    "creation_date" datetime NOT NULL
)
;

CREATE TABLE "report" (
    "bssid" varchar(25) NOT NULL PRIMARY KEY,
    "password" varchar(128) NOT NULL,
    "date" datetime NOT NULL,
    "success" bool NOT NULL
)
;
EOF

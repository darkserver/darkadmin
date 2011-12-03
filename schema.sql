-- sql schema for darkadmin
-- written by morsik

-- module: accounts
-- password is for web panel, not ssh account

CREATE TABLE `accounts_data` (
	`id`         smallint(2)  unsigned NOT NULL, 
	`uid`        smallint(2)  unsigned NOT NULL,
	`password`   char(32)     DEFAULT NULL, -- hash with salt
	`salt`       char(8)      DEFAULT NULL, -- salt
	`first_name` varchar(20)  NOT NULL,
	`last_name`  varchar(30)  NOT NULL,
	`birth_date` date         DEFAULT NULL,
	`phone`      varchar(12)  DEFAULT NULL,
	`country`    varchar(2)   DEFAULT NULL,
	`city`       varchar(30)  DEFAULT NULL,
	`postcode`   varchar(10)  DEFAULT NULL,
	`address`    varchar(128) DEFAULT NULL,
	`mail`       varchar(32)  NOT NULL,
	`jid`        varchar(32)  DEFAULT NULL,

	`created`    date         DEFAULT NULL,
	`valid`      date         DEFAULT NULL,
	`enabled`    tinyint(1)   DEFAULT '0',
	`blocked`    tinyint(1)   DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `mail` (`mail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- services
-- all available services which should be run on boot

CREATE TABLE `services` (
	`id`        smallint(2) unsigned NOT NULL,
	`uid`       smallint(2) unsigned NOT NULL,
	`type`      varchar(16) DEFAULT NULL,
	`domain`    varchar(64) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `domain` (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

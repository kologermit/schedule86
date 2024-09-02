CREATE TABLE IF NOT EXISTS `config` (
  `theme` varchar(5000) NOT NULL,
  `data` varchar(5000) NOT NULL
);

INSERT INTO `config` (`theme`, `data`) VALUES
	('call_schedule', '["08:30-09:10","09:20-10:00","10:20-11:00","11:20-12:00","12:20-13:00","13:10-13:50","14:00-14:40"]'),
	('holidays', 'Информация отсутствует'),
	('classes', '{"5": "АБВГМ","6": "АБВГМ","7": "АБВГДМ","8": "АБВГД","9": "АБВГДК","10": "АБВ","11": "АБВ"}'),
	('teachers', '{"kologermit@gmail.com": 847721936,"vladfanck@gmail.com": 1294113685,"ankologer@gmail.com": 317137872,"success11@mail.ru": 475457558}'),
	('admins', '[1294113685]');

CREATE TABLE IF NOT EXISTS `schedule_classes` (
  `parallel` int NOT NULL,
  `symbol` char(50) NOT NULL,
  `schedule` varchar(5000) NOT NULL DEFAULT '{"standart": {"ПОНЕДЕЛЬНИК": [], "ВТОРНИК": [], "СРЕДА": [], "ЧЕТВЕРГ": [], "ПЯТНИЦА": [], "СУББОТА": []}, "edited": {}}',
  `subscribe` varchar(5000) NOT NULL DEFAULT '[]'
);


CREATE TABLE IF NOT EXISTS `teachers` (
  `name` tinytext NOT NULL,
  `subscribe` varchar(5000) NOT NULL DEFAULT '[]',
  `schedule` varchar(5000) NOT NULL DEFAULT '{"standart": {"ПОНЕДЕЛЬНИК": [], "ВТОРНИК": [], "СРЕДА": [], "ЧЕТВЕРГ": [], "ПЯТНИЦА": [], "СУББОТА": []}, "edited": {}}'
);


CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL,
  `name` varchar(5000) NOT NULL,
  `status` varchar(5000) NOT NULL DEFAULT 'menu',
  `settings` varchar(5000) NOT NULL DEFAULT '{"subscribe": [], "commands": []}'
);

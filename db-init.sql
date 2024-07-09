CREATE TABLE IF NOT EXISTS `config` (
  `theme` text NOT NULL,
  `data` text NOT NULL
);

INSERT INTO `config` (`theme`, `data`) VALUES
	('call_schedule', '["08:30-09:10",\r\n"09:20-10:00",\r\n"10:20-11:00",\r\n"11:20-12:00",\r\n"12:20-13:00",\r\n"13:10-13:50",\r\n"14:00-14:40"]'),
	('holidays', '<b>Сентябрь:</b>\r\nВоскресенья: 3, 10, 17, 24\r\nКаникулы: Отсутствуют\r\n\r\n<b>Октябрь:</b>\r\nВоскресенья: 1, 8, 15, 22, 29\r\nКаникулы: Отсутствуют\r\n\r\n<b>Ноябрь:</b>\r\nВоскресенья: 5, 12, 19, 26\r\nПраздники: 4\r\nКаникулы: 20 - 26\r\n\r\n<b>Декабрь:</b> \r\nВоскресенья: 3, 10, 17, 24, 31\r\n\r\n<b>Январь:</b> \r\nВоскресенья: 7, 14, 21, 28\r\nКаникулы: 1 - 8\r\n\r\n<b>Февраль:</b>\r\nВоскресенья: 4, 11, 18, 25\r\nПраздники: 23\r\nКаникулы: 26 Февраля - 3 Марта\r\n\r\n<b>Март:</b>\r\nВоскресенья: 3, 10, 17, 24\r\nПраздники: 8\r\n\r\n<b>Апрель:</b>\r\nВоскресенья: 7, 14, 21, 28\r\nКаникулы: Отсутствуют\r\n\r\n<b>Май:</b>\r\nВоскресенья: 5, 12, 19, 26\r\nПраздники: 1, 9\r\nКаникулы: 10, 11, 27+'),
	('classes', '{\r\n"5": "АБВГМ",\r\n"6": "АБВГМ",\r\n"7": "АБВГДМ",\r\n"8": "АБВГД",\r\n"9": "АБВГДК",\r\n"10": "АБВ",\r\n"11": "АБВ"\r\n}'),
	('teachers', '{\r\n"kologermit@gmail.com": 847721936,\r\n"vladfanck@gmail.com": 1294113685,\r\n"ankologer@gmail.com": 317137872,\r\n"success11@mail.ru": 475457558\r\n}'),
	('admins', '[1294113685]');

CREATE TABLE IF NOT EXISTS `schedule_classes` (
  `parallel` int NOT NULL,
  `symbol` char(50) NOT NULL,
  `schedule` text NOT NULL DEFAULT '{"standart": {"ПОНЕДЕЛЬНИК": [], "ВТОРНИК": [], "СРЕДА": [], "ЧЕТВЕРГ": [], "ПЯТНИЦА": [], "СУББОТА": []}, "edited": {}}',
  `subscribe` text NOT NULL DEFAULT '[]'
);


CREATE TABLE IF NOT EXISTS `teachers` (
  `name` tinytext NOT NULL,
  `subscribe` text NOT NULL DEFAULT '[]',
  `schedule` text NOT NULL DEFAULT '{"standart": {"ПОНЕДЕЛЬНИК": [], "ВТОРНИК": [], "СРЕДА": [], "ЧЕТВЕРГ": [], "ПЯТНИЦА": [], "СУББОТА": []}, "edited": {}}'
);


CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL,
  `name` tinytext NOT NULL,
  `status` tinytext NOT NULL DEFAULT 'menu',
  `settings` text NOT NULL DEFAULT `{"subscribe": [], "commands": []}`
);
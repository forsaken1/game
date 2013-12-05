import MySQLdb

DB_NAME = "game"

def create_db():
	con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='')	
	cursor = con.cursor()
	cursor.execute('DROP DATABASE IF EXISTS %s'% DB_NAME)	
	cursor.execute('CREATE DATABASE %s'% DB_NAME)
	cursor.execute('use ' + DB_NAME)   
	sql = '''CREATE TABLE IF NOT EXISTS `users` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`sid` varchar(64) CHARACTER SET latin1,
			`login` varchar(255) CHARACTER SET latin1 NOT NULL,
			`password` LONGBLOB,
			PRIMARY KEY (`id`),
			KEY `id` (`id`)
			)DEFAULT CHARSET=utf8 AUTO_INCREMENT=2  
			ENGINE=INNODB;
		   '''
	cursor.execute(sql)    
	sql = '''CREATE TABLE IF NOT EXISTS `messages` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`login` varchar(255) CHARACTER SET latin1 NOT NULL,
			`text` LONGTEXT CHARACTER SET utf8 NOT NULL,
			`time` int(11) NOT NULL,
			`game_id` int(11),
			PRIMARY KEY (`id`)
			)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 
			ENGINE=INNODB;
		   '''
	cursor.execute(sql)             
	sql = '''CREATE TABLE IF NOT EXISTS `games` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`name` varchar(256) CHARACTER SET latin1 NOT NULL,
			`map` int(11) NOT NULL,
			`maxPlayers` int(11) NOT NULL,
			`status` bit(1) DEFAULT b'1' NOT NULL,
			`accel` float(11) NOT NULL,
			`maxVelocity` float(11) NOT NULL,
			`friction` float(11) NOT NULL,
			`gravity` float(11) NOT NULL,												
			PRIMARY KEY (`id`)
			)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
			ENGINE=INNODB;
		   '''
	cursor.execute(sql)             
	sql = '''CREATE TABLE IF NOT EXISTS `maps` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`name` varchar(256) CHARACTER SET latin1 NOT NULL,
			`map` LONGBLOB,
			`maxPlayers` int(11) NOT NULL,
			PRIMARY KEY (`id`)
			)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
			ENGINE=INNODB;					
		   '''
	cursor.execute(sql)
	sql = '''CREATE TABLE IF NOT EXISTS `user_game` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`pid` varchar(64) CHARACTER SET latin1,
			`login` varchar(255) CHARACTER SET latin1 NOT NULL,
			`game_id` int(11) NOT NULL,
			PRIMARY KEY (`id`)
			)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
			ENGINE=INNODB;				
		   '''
	cursor.execute(sql)		
	con.close()
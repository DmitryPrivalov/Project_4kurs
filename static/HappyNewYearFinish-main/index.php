<?php

spl_autoload_register(function ($class) {
    include 'classes/' . $class . '.php';
});




$currentDate = date('m.d', time());
$currentDateArray = explode('.', $currentDate);

$currentMounth = $currentDateArray[0];
$currentDay = $currentDateArray[1];
$PDO = PdoConnect::getInstance();
/*$sql = "
INSERT INTO goods (`name`,`price`,`image`) VALUES  ('Porsche 911 Carrera', 12000000, 'static/img/1.jpg'),
    ('Porsche Cayenne', 8000000, 'static/img/2.jpg'),
    ('BMW X5', 7000000, 'static/img/3.jpg'),
    ('BMW 3 Series', 4500000, 'static/img/4.jpg'),
    ('Mercedes-Benz S-Class', 10000000, 'static/img/5.jpg'),
    ('Mercedes-Benz C-Class', 5500000, 'static/img/6.jpg'),
    ('Mercedes-Benz GLE', 7500000, 'static/img/7.jpg')";
 $res = $PDO -> PDO->query($sql);


   /* $sql = "
CREATE TABLE IF NOT EXISTS orders
(
id int NOT NULL AUTO_INCREMENT,
fio varchar(255) NOT NULL,
phone varchar(255) NOT NULL,
email varchar(255) NOT NULL,
comment text NOT NULL,
product_id int NOT NULL,
PRIMARY KEY (id)
) CHARSET=utf8
";
$result = $PDO->PDO->query($sql);

$PDO = PdoConnect::getInstance();
$sql = "
CREATE TABLE IF NOT EXISTS goods
(
id int NOT NULL AUTO_INCREMENT,
name varchar(255) NOT NULL,
price varchar(255) NOT NULL,
image varchar(255) NOT NULL,
PRIMARY KEY (id)
) CHARSET=utf8
";*/

	$result = $PDO->PDO->query("
		SELECT * FROM `goods`
	");

	$products = array();

	while ($productInfo = $result->fetch()) {
		$products[] = $productInfo;
	}
	
	

	include 'index3.php';

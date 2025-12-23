<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport">
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    <title>Автосалон</title>
    <script src="static/js/jquery-3.4.1.min.js"></script>
	<script src="static/js/slick.js"></script>
	<script src="static/js/script.js"></script>
    
	
	<link href="static/css/style1.css" rel="stylesheet" type="text/css">
</head>
<body>

<header class="header">
    <div class="container">
        <div class="header__wrapper">

            <div class="header__block">
                <a href="/" class="header__logo">
                    <img src="img/logo.png" alt="">
                </a>
            </div>
            <!--/header__block-->

            <nav class="nav">
                <a href="../index.html" class="nav__link active" >Главная</a>
                <a href="..//carsell24x7-main/index.html#contact" class="nav__link" >Контакты</a>
            </nav>

            <div class="header__block">
                <div class="header__lng">
                    <a href="index1.html" class="header__lng-link active">
                        Войти
                    </a>
                    <a href="#" class="header__lng-link active">/</a>
                    <a href="index1.html" class="header__lng-link "> Зарегистрироваться </a>
                </div>
            </div>
        </div>
        <!--/header__wrapper-->

    </div>
    <!--/container-->
</header>

<section class="product-box">
<a  id="catalog-link">Каталог</a>
<div class="filter-container">
        <div class="filter-item">
            <label for="filter-price">Цена:</label>
            <select id="filter-price">
                <option value="asc">По возрастанию</option>
                <option value="desc">По убыванию</option>
               
            </select>
        </div>
        <div class="filter-item">
            <label for="filter-name">Название:</label>
            <select id="filter-name">
                <option value="asc">По возрастанию</option>
                <option value="desc">По убыванию</option>
                
            </select>
        </div>
    </div>
			<div class= " contener"> 
			<div class="row" id="product-container">
            <?php
function bubbleSort($products, $field) {
    $n = count($products);
    for ($i = 0; $i < $n - 1; $i++) {
        for ($j = 0; $j < $n - $i - 1; $j++) {
            if ($field === 'name') {
                if (strcmp($products[$j][$field], $products[$j + 1][$field]) > 0) {
                    $temp = $products[$j];
                    $products[$j] = $products[$j + 1];
                    $products[$j + 1] = $temp;
                }
            } else if ($field === 'price') {
                if ($products[$j][$field] > $products[$j + 1][$field]) {
                    $temp = $products[$j];
                    $products[$j] = $products[$j + 1];
                    $products[$j + 1] = $temp;
                }
            }
        }
    }
    return $products;
}
?>
				<?foreach ($products as $product):?>
					<div class="col-xs-6 col-sm-4 col-md-3 col-lg-3 product-parent" data-id="<?=$product['id']?>">
						<div class="product">
							<div class="product-pic" style="background: url('<?=$product['image']?>') no-repeat; background-color: white; background-size: auto 100%; object-fit: cover;  width: 250px; background-position: center"></div>
							<span class="product-name"><?=$product['name']?></span>
							<span class="product_price"><?=$product['price']?> руб.</span>
							<button class="js_buy">Купить</button>
						</div>
					</div>
				<?endforeach?>
			</div>
				</div>
		</section>
		<footer>
			
		</footer>
	</div>
	<div class="overlay js_overlay"></div>
	<div class="popup">
		<h3>Оформление заказа</h3><i class="fas fa-times close-popup js_close-popup"></i>
		<div class='js_error'></div>
		<input type="hidden" name="product-id">
		<input type="text" name="fio" placeholder="Ваше имя">
		<input type="text" name="phone" placeholder="Телефон">
		<input type="text" name="email" placeholder="e-mail">
		<textarea placeholder="Комментарий" name="comment"></textarea>
		<button class="js_send">Отправить</button>
	</div>
    
                © 2024 Все права защищены 
            </p>
            <div class="footer__soc">
                <a href="#" class="footer__soc-link">
                    <img src="img/linkedin.svg" alt="">
                </a>
                <a href="#" class="footer__soc-link">
                    <img src="img/facebook.svg" alt="">
                </a>
                <a href="https://instagram.com" target="_blank" class="footer__soc-link">
                    <img src="img/instagram.svg" alt="">
                </a>
            </div>
        </div>
    </div>
</footer>

<script>
    
    const priceFilter = document.getElementById("filter-price");
    const nameFilter = document.getElementById("filter-name");
    const productContainer = document.getElementById("product-container");

    function filterProducts() {
        const field = this.id === 'filter-price' ? 'price' : 'name'; // Определяем поле для сортировки
        const order = this.value; // Получаем порядок сортировки (asc или desc)

        // Отправляем AJAX-запрос для сортировки товаров
        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'sort.php'); // Добавьте обработчик на сервере
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function () {
            if (xhr.status === 200) {
                // Обновляем содержимое контейнера с отсортированными товарами
                productContainer.innerHTML = xhr.responseText; 
            } else {
                console.error('Ошибка AJAX-запроса: ' + xhr.status);
            }
        };
        xhr.send('field=' + field + '&order=' + order);
    }

    // Обработчики изменения фильтров
    priceFilter.addEventListener('change', filterProducts);
    nameFilter.addEventListener('change', filterProducts);

</script>
</body>
</html>
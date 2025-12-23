<?php
require_once 'classes/PdoConnect.php'; 

if (isset($_POST['field']) && isset($_POST['order'])) {
    $field = $_POST['field'];
    $order = $_POST['order'];

    $PDO = PdoConnect::getInstance();
    

    $result = $PDO->PDO->query("SELECT * FROM `goods` ORDER BY `$field` $order");
    $products = $result->fetchAll(PDO::FETCH_ASSOC);

    foreach ($products as $product) {
        ?>
        <div class="col-xs-6 col-sm-4 col-md-3 col-lg-3 product-parent" data-id="<?= $product['id'] ?>">
            <div class="product">
                <div class="product-pic" style="background: url('<?= $product['image'] ?>') no-repeat; background-color: white; background-size: auto 100%;  width: 250px; background-position: center"></div>
                <span class="product-name"><?= $product['name'] ?></span>
                <span class="product_price"><?= $product['price'] ?> руб.</span>
                <button class="js_buy">Купить</button>
            </div>
        </div>
        <?php
    }
}
?>
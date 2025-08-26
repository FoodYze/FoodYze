<?php
// db_connect.php
// Este arquivo contém os detalhes de conexão com o banco de dados
// e estabelece a conexão.

// --- CONFIGURAÇÕES DO BANCO DE DADOS ---
// O endereço do servidor do banco de dados. "localhost" significa que está na mesma máquina.
$servername = "localhost";

// O nome de usuário para acessar o banco de dados. "root" é o padrão do XAMPP.
$username = "root";

// A senha para o usuário. A senha do usuário "root" no XAMPP é vazia por padrão.
$password = "";

// O nome do banco de dados que criamos no passo anterior.
$dbname = "site_mygely";


// --- CRIAÇÃO DA CONEXÃO ---
// A linha abaixo tenta se conectar ao banco de dados usando as configurações acima.
$conn = new mysqli($servername, $username, $password, $dbname);


// --- VERIFICAÇÃO DA CONEXÃO ---
// É crucial verificar se a conexão foi bem-sucedida.
// Se houver um erro de conexão ($conn->connect_error), o script para e exibe a mensagem de erro.
if ($conn->connect_error) {
    // A função die() interrompe a execução do script imediatamente.
    die("Falha na conexão com o banco de dados: " . $conn->connect_error);
}

// Se o script chegar até aqui sem parar, significa que a conexão foi um sucesso!
?>
<?php
// PARTE 1: O CÉREBRO (LÓGICA PHP)

// session_start() deve ser a PRIMEIRA coisa no seu script.
// Ela inicia ou resume uma sessão, que é como uma "memória" temporária no servidor para cada visitante.
session_start();

// Se o usuário JÁ ESTIVER logado, não precisa fazer login de novo.
// Redirecionamos ele direto para o painel.
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    header('Location: dashboard.php');
    exit;
}

// Inclui nossa "chave" de conexão com o banco de dados.
require_once 'db_connect.php';

// O código abaixo só executa QUANDO o formulário de login é enviado.
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = trim($_POST['password']);
    $error = null;

    if (!empty($username) && !empty($password)) {
        // 1. PREPARAR A CONSULTA PARA BUSCAR O USUÁRIO
        // Desta vez, usamos SELECT para buscar dados, em vez de INSERT.
        // Buscamos o usuário cujo 'username' seja igual ao que foi digitado.
        $query = "SELECT id, username, password FROM usuarios WHERE username = ?";
        $stmt = $conn->prepare($query);
        $stmt->bind_param("s", $username);

        // 2. EXECUTAR A CONSULTA
        $stmt->execute();
        $result = $stmt->get_result(); // Pega os resultados da consulta.

        // 3. VERIFICAR SE O USUÁRIO FOI ENCONTRADO
        // Se a consulta retornou exatamente 1 linha, significa que encontramos o usuário.
        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc(); // Pega os dados do usuário e coloca em um array.

            // 4. VERIFICAR A SENHA (O PASSO MÁGICO!)
            // A função password_verify() compara a senha digitada ($password)
            // com a senha criptografada que está no banco ($user['password']).
            if (password_verify($password, $user['password'])) {
                // Senha correta!

                // 5. INICIAR A SESSÃO E ARMAZENAR DADOS
                // Armazenamos na "memória da sessão" que o usuário está logado,
                // além de seu ID e nome de usuário para usar em outras páginas.
                session_regenerate_id(); // Medida de segurança
                $_SESSION['loggedin'] = true;
                $_SESSION['id'] = $user['id'];
                $_SESSION['username'] = $user['username'];

                // Redireciona o usuário para sua página de painel.
                header("Location: dashboard.php");
                exit();
            } else {
                // Senha incorreta.
                $error = "Senha inválida.";
            }
        } else {
            // Usuário não encontrado.
            $error = "Nenhum usuário encontrado com esse nome.";
        }
        $stmt->close();
    } else {
        $error = "Por favor, preencha todos os campos.";
    }
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="form-container">
        <h2>Acessar sua Conta</h2>

        <?php if (isset($_GET['status']) && $_GET['status'] == 'success') { echo "<p class='success'>Cadastro realizado com sucesso! Faça o login.</p>"; } ?>
        
        <?php if (isset($error)) { echo "<p class='error'>$error</p>"; } ?>

        <form action="login.php" method="post">
            <label for="username">Nome de Usuário:</label>
            <input type="text" name="username" id="username" required>

            <label for="password">Senha:</label>
            <input type="password" name="password" id="password" required>

            <button type="submit">Entrar</button>
        </form>
        <p>Não tem uma conta? <a href="register.php">Cadastre-se aqui</a>.</p>
    </div>
</body>
</html>

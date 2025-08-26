<?php
// O segurança da nossa Sala VIP.

// Inicia a sessão para que possamos acessar as variáveis de sessão.
session_start();

// A VERIFICAÇÃO DE SEGURANÇA:
// A função isset() verifica se a variável 'loggedin' existe na sessão.
// O 'loggedin' === true verifica se o valor é exatamente 'true'.
// Se qualquer uma dessas condições for falsa, significa que o usuário NÃO está logado.
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    // Se não estiver logado, redireciona de volta para a página de login.
    header('Location: login.php');
    exit; // Garante que o resto do script não seja executado.
}

// Se o script chegou até aqui, o usuário está autenticado!
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel do Usuário</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="dashboard-container">
        <h1>Bem-vindo(a) de volta, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h1>
        <p>Esta é a sua página de painel. Apenas usuários autenticados podem vê-la.</p>
        <p>Seu ID de usuário é: <?php echo $_SESSION['id']; ?></p>
        <br>
        <a href="logout.php" class="logout-button">Sair (Logout)</a>
    </div>
</body>
</html>

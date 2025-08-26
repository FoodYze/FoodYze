<?php
// PARTE 1: O CÉREBRO (LÓGICA PHP)

// Inclui o nosso script de conexão. É como pegar a "chave" para abrir o banco de dados.
require_once 'db_connect.php';

// Esta condição verifica se a página foi acessada através do envio de um formulário (método POST).
// Ou seja, o código aqui dentro só roda QUANDO o usuário clica no botão "Cadastrar".
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    // 1. RECEBER E LIMPAR OS DADOS
    // A função trim() remove espaços em branco extras do início e do fim.
    $username = trim($_POST['username']);
    $password = trim($_POST['password']);
    $error = null; // Variável para armazenar mensagens de erro

    // 2. VALIDAÇÃO SIMPLES
    // Verifica se os campos não estão vazios.
    if (empty($username) || empty($password)) {
        $error = "Por favor, preencha todos os campos.";
    } else {
        // 3. CRIPTOGRAFIA DA SENHA (PASSO DE SEGURANÇA CRÍTICO!)
        // NUNCA, JAMAIS armazene senhas em texto puro.
        // A função password_hash() cria um "código secreto" seguro para a senha.
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);

        // 4. PREPARAR E EXECUTAR A INSERÇÃO NO BANCO
        // Usamos "Prepared Statements" (prepare e bind_param) para evitar um tipo de ataque chamado SQL Injection.
        // É uma medida de segurança que separa a "instrução" dos "dados".
        $query = "INSERT INTO usuarios (username, password) VALUES (?, ?)";
        $stmt = $conn->prepare($query);

        // "ss" significa que estamos enviando duas variáveis do tipo String (texto).
        $stmt->bind_param("ss", $username, $hashed_password);

        // Tenta executar a query preparada.
        if ($stmt->execute()) {
            // Se o cadastro deu certo, redireciona o usuário para a página de login.
            // Enviamos uma "pista" na URL (?status=success) para mostrar uma mensagem de sucesso lá.
            header("Location: login.php?status=success");
            exit(); // Encerra o script para garantir que o redirecionamento aconteça.
        } else {
            // Se deu erro, verificamos se é por causa de um usuário duplicado.
            if ($conn->errno == 1062) { // 1062 é o código de erro para "Entrada duplicada".
                $error = "Este nome de usuário já existe. Por favor, escolha outro.";
            } else {
                $error = "Erro ao realizar o cadastro. Tente novamente. Erro: " . $stmt->error;
            }
        }
        $stmt->close(); // Fecha o statement
    }
    $conn->close(); // Fecha a conexão
}
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Cadastro de Usuário</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="form-container">
        <h2>Criar Nova Conta</h2>

        <?php if (isset($error)) { echo "<p class='error'>$error</p>"; } ?>

        <form action="register.php" method="post">
            <label for="username">Nome de Usuário:</label>
            <input type="text" name="username" id="username" required>

            <label for="password">Senha:</label>
            <input type="password" name="password" id="password" required>

            <button type="submit">Cadastrar</button>
        </form>
        <p>Já tem uma conta? <a href="login.php">Faça login aqui</a>.</p>
    </div>
</body>
</html>

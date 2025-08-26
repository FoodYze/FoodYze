<?php
// O processo de check-out do hotel.

// 1. Inicia a sessão para poder manipulá-la.
session_start();

// 2. Limpa todas as variáveis da sessão.
// É como pegar a ficha do hóspede e apagar tudo o que estava escrito nela.
$_SESSION = array();

// 3. Destrói a sessão.
// Isso destrói o arquivo da sessão no servidor. É como rasgar a ficha do hóspede.
session_destroy();

// 4. Redireciona o usuário para a página de login.
// O check-out está completo, o ex-hóspede é levado para a entrada do hotel.
header("Location: login.php");
exit;
?>

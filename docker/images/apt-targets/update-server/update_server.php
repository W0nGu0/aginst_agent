<?php
// 软件更新服务器 - 包含预设漏洞
session_start();

// 预设漏洞：弱认证
$valid_users = array(
    'updateadmin' => 'update123',
    'admin' => 'admin',
    'guest' => 'guest'
);

$authenticated = false;
if (isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    if (isset($valid_users[$username]) && $valid_users[$username] === $password) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
        $authenticated = true;
    }
}

if (isset($_SESSION['authenticated']) && $_SESSION['authenticated']) {
    $authenticated = true;
}

// 预设漏洞：目录遍历
if (isset($_GET['file']) && $authenticated) {
    $file = $_GET['file'];
    // 漏洞：没有过滤目录遍历
    $filepath = "/var/updates/packages/" . $file;
    if (file_exists($filepath)) {
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        readfile($filepath);
        exit;
    }
}

// 预设漏洞：代码注入
if (isset($_POST['update_script']) && $authenticated) {
    $script = $_POST['update_script'];
    // 漏洞：直接执行用户输入
    $output = shell_exec($script);
    echo "<pre>Script Output: " . htmlspecialchars($output) . "</pre>";
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>ACME Corp - 软件更新服务器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .admin-panel { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        .vulnerability { color: red; font-size: 12px; }
    </style>
</head>
<body>
    <h1>ACME Corp 软件更新服务器</h1>
    
    <?php if (!$authenticated): ?>
    <div class="login-form">
        <h2>管理员登录</h2>
        <form method="post">
            <p>
                <label>用户名:</label><br>
                <input type="text" name="username" required>
                <span class="vulnerability">(提示: updateadmin)</span>
            </p>
            <p>
                <label>密码:</label><br>
                <input type="password" name="password" required>
                <span class="vulnerability">(提示: update123)</span>
            </p>
            <p><input type="submit" value="登录"></p>
        </form>
    </div>
    <?php else: ?>
    <div class="admin-panel">
        <h2>欢迎, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
        
        <h3>软件包下载</h3>
        <p>下载软件包: <a href="?file=../config/config.php">配置文件</a> (漏洞演示)</p>
        <form method="get">
            <input type="text" name="file" placeholder="输入文件路径" value="../config/config.php">
            <input type="submit" value="下载">
        </form>
        
        <h3>更新脚本执行</h3>
        <form method="post">
            <textarea name="update_script" rows="4" cols="50" placeholder="输入更新脚本命令">ls -la /var/updates/</textarea><br>
            <input type="submit" value="执行脚本">
        </form>
        
        <h3>文件上传</h3>
        <p><a href="upload.php">上传新的软件包</a></p>
        
        <p><a href="?logout=1">退出登录</a></p>
    </div>
    <?php endif; ?>
    
    <?php
    if (isset($_GET['logout'])) {
        session_destroy();
        header('Location: index.php');
        exit;
    }
    ?>
</body>
</html>

<?php
// 开发环境控制面板 - 包含预设漏洞
session_start();

// 预设漏洞：弱认证
$valid_users = array(
    'developer' => 'dev123',
    'admin' => 'admin123',
    'root' => 'root123',
    'test' => 'test123'
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

// 预设漏洞：命令执行
if (isset($_POST['command']) && $authenticated) {
    $command = $_POST['command'];
    // 漏洞：直接执行用户输入的命令
    $output = shell_exec($command . " 2>&1");
    echo "<div class='command-output'><h4>命令执行结果:</h4><pre>" . htmlspecialchars($output) . "</pre></div>";
}

// 预设漏洞：文件读取
if (isset($_GET['file']) && $authenticated) {
    $file = $_GET['file'];
    // 漏洞：没有过滤目录遍历
    $filepath = "/var/dev/" . $file;
    if (file_exists($filepath)) {
        echo "<div class='file-content'><h4>文件内容: " . htmlspecialchars($file) . "</h4>";
        echo "<pre>" . htmlspecialchars(file_get_contents($filepath)) . "</pre></div>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>开发环境控制面板</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .dashboard { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        .vulnerability { color: red; font-size: 12px; }
        .command-output { background: #000; color: #0f0; padding: 15px; margin: 15px 0; }
        .file-content { background: #fff; border: 1px solid #ddd; padding: 15px; margin: 15px 0; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>开发环境控制面板</h1>
    
    <?php if (!$authenticated): ?>
    <div class="login-form">
        <h2>开发者登录</h2>
        <form method="post">
            <p>
                <label>用户名:</label><br>
                <input type="text" name="username" required>
                <span class="vulnerability">(提示: developer, admin, root, test)</span>
            </p>
            <p>
                <label>密码:</label><br>
                <input type="password" name="password" required>
                <span class="vulnerability">(提示: dev123, admin123, root123, test123)</span>
            </p>
            <p><input type="submit" value="登录"></p>
        </form>
    </div>
    <?php else: ?>
    <div class="dashboard">
        <h2>欢迎, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
        
        <div class="section">
            <h3>命令执行</h3>
            <form method="post">
                <textarea name="command" rows="3" cols="60" placeholder="输入系统命令">ls -la /var/dev/</textarea><br>
                <input type="submit" value="执行命令">
                <span class="vulnerability">(命令注入测试: ; cat /etc/passwd)</span>
            </form>
        </div>
        
        <div class="section">
            <h3>文件浏览</h3>
            <p>快速访问:</p>
            <ul>
                <li><a href="?file=code/medical_app/config.py">应用配置文件</a></li>
                <li><a href="?file=secrets/api_keys.txt">API密钥文件</a></li>
                <li><a href="?file=config/database.conf">数据库配置</a></li>
                <li><a href="?file=../../../etc/passwd">系统密码文件</a> (漏洞演示)</li>
            </ul>
            <form method="get">
                <input type="text" name="file" placeholder="输入文件路径" value="secrets/api_keys.txt">
                <input type="submit" value="读取文件">
            </form>
        </div>
        
        <div class="section">
            <h3>Git仓库信息</h3>
            <p>当前项目: medical_app</p>
            <p>分支: main</p>
            <p>最后提交: Initial commit with secrets</p>
            <p><a href="?file=code/medical_app/.git/config">Git配置</a></p>
            <p><a href="?file=code/medical_app/.git/logs/HEAD">Git日志</a></p>
        </div>
        
        <div class="section">
            <h3>环境信息</h3>
            <p>服务器: dev.company.local</p>
            <p>操作系统: Ubuntu 20.04</p>
            <p>PHP版本: <?php echo phpversion(); ?></p>
            <p>调试模式: 开启</p>
            <p>错误报告: 完全开启</p>
        </div>
        
        <div class="section">
            <h3>数据库连接</h3>
            <p>主数据库: medical-database:5432</p>
            <p>用户: med_admin</p>
            <p>密码: MedDB2024!</p>
            <p>状态: <span style="color: green;">已连接</span></p>
        </div>
        
        <div class="section">
            <h3>API服务</h3>
            <p>内部API: http://api.company.local</p>
            <p>API密钥: med_api_key_12345_secret</p>
            <p>外部服务令牌: ext_service_token_abcdef</p>
        </div>
        
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
    
    <div class="vulnerability">
        <h4>预设漏洞说明:</h4>
        <ul>
            <li>弱密码认证: 多个弱密码账户</li>
            <li>命令注入: 直接执行用户输入命令</li>
            <li>目录遍历: 可以读取任意文件</li>
            <li>敏感信息暴露: 显示数据库密码和API密钥</li>
            <li>Git信息泄露: 暴露版本控制信息</li>
            <li>调试信息泄露: 开启调试模式</li>
        </ul>
    </div>
</body>
</html>

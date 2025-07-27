<?php
// 备份服务器Web界面 - 包含预设漏洞
session_start();

// 预设漏洞：弱认证
$valid_users = array(
    'backupadmin' => 'backup2024',
    'admin' => 'admin123',
    'backup' => 'backup123',
    'operator' => 'operator123'
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
if (isset($_POST['backup_command']) && $authenticated) {
    $command = $_POST['backup_command'];
    // 漏洞：直接执行用户输入的命令
    $output = shell_exec($command . " 2>&1");
    echo "<div class='command-output'><h4>备份命令执行结果:</h4><pre>" . htmlspecialchars($output) . "</pre></div>";
}

// 预设漏洞：文件下载
if (isset($_GET['download']) && $authenticated) {
    $file = $_GET['download'];
    // 漏洞：没有过滤目录遍历
    $filepath = "/var/backup/data/" . $file;
    if (file_exists($filepath)) {
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        readfile($filepath);
        exit;
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>备份服务器管理</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .dashboard { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        .vulnerability { color: red; font-size: 12px; }
        .command-output { background: #000; color: #0f0; padding: 15px; margin: 15px 0; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .backup-item { padding: 10px; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>备份服务器管理系统</h1>
    
    <?php if (!$authenticated): ?>
    <div class="login-form">
        <h2>管理员登录</h2>
        <form method="post">
            <p>
                <label>用户名:</label><br>
                <input type="text" name="username" required>
                <span class="vulnerability">(提示: backupadmin, admin, backup)</span>
            </p>
            <p>
                <label>密码:</label><br>
                <input type="password" name="password" required>
                <span class="vulnerability">(提示: backup2024, admin123, backup123)</span>
            </p>
            <p><input type="submit" value="登录"></p>
        </form>
    </div>
    <?php else: ?>
    <div class="dashboard">
        <h2>欢迎, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
        
        <div class="section">
            <h3>备份命令执行</h3>
            <form method="post">
                <textarea name="backup_command" rows="3" cols="60" placeholder="输入备份命令">rsync -av /var/backup/data/ /mnt/backup/</textarea><br>
                <input type="submit" value="执行备份命令">
                <span class="vulnerability">(命令注入测试: ; cat /etc/passwd)</span>
            </form>
        </div>
        
        <div class="section">
            <h3>备份文件列表</h3>
            <?php
            $backup_files = array(
                'medical_db_backup_20240127.sql' => '医疗数据库备份',
                'his_system_backup_20240127.tar.gz' => 'HIS系统备份',
                'pacs_images_backup_20240127.tar' => 'PACS影像备份',
                'lis_data_backup_20240127.zip' => 'LIS数据备份',
                'config_backup_20240127.tar.gz' => '配置文件备份',
                '../../../etc/passwd' => '系统密码文件 (漏洞演示)'
            );
            
            foreach ($backup_files as $filename => $description) {
                echo "<div class='backup-item'>";
                echo "<strong>" . htmlspecialchars($filename) . "</strong><br>";
                echo htmlspecialchars($description) . "<br>";
                echo "<a href='?download=" . urlencode($filename) . "'>[下载]</a>";
                echo "</div>";
            }
            ?>
        </div>
        
        <div class="section">
            <h3>SMB共享访问</h3>
            <p>SMB共享路径: \\\\backup-server\\backup</p>
            <p>用户名: backupadmin</p>
            <p>密码: backup2024</p>
            <p>权限: 读写</p>
            <p><span class="vulnerability">注意: SMB配置允许匿名访问</span></p>
        </div>
        
        <div class="section">
            <h3>备份计划</h3>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr><th>备份任务</th><th>计划时间</th><th>状态</th><th>最后执行</th></tr>
                <tr><td>医疗数据库</td><td>每日 02:00</td><td>启用</td><td>2024-01-27 02:00</td></tr>
                <tr><td>HIS系统</td><td>每日 03:00</td><td>启用</td><td>2024-01-27 03:00</td></tr>
                <tr><td>PACS影像</td><td>每周日 01:00</td><td>启用</td><td>2024-01-21 01:00</td></tr>
                <tr><td>LIS数据</td><td>每日 04:00</td><td>启用</td><td>2024-01-27 04:00</td></tr>
                <tr><td>配置文件</td><td>每日 05:00</td><td>启用</td><td>2024-01-27 05:00</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>系统信息</h3>
            <p>服务器: backup.company.local</p>
            <p>存储空间: 2TB (已使用 45%)</p>
            <p>备份保留期: 30天</p>
            <p>加密状态: <span style="color: red;">未启用</span></p>
            <p>压缩状态: 启用</p>
        </div>
        
        <div class="section">
            <h3>数据库连接信息</h3>
            <p>主数据库: medical-database:5432</p>
            <p>备份用户: backup_user</p>
            <p>备份密码: backup_db_pass_2024</p>
            <p>备份脚本: /var/backup/scripts/backup_script.sh</p>
        </div>
        
        <div class="section">
            <h3>网络共享</h3>
            <p>SMB端口: 445, 139</p>
            <p>FTP端口: 21</p>
            <p>RSYNC端口: 873</p>
            <p>SSH端口: 22</p>
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
            <li>目录遍历: 可以下载任意文件</li>
            <li>SMB配置不当: 允许匿名访问</li>
            <li>备份未加密: 敏感数据明文存储</li>
            <li>敏感信息暴露: 显示数据库密码</li>
            <li>权限配置不当: 备份文件权限过宽</li>
        </ul>
    </div>
</body>
</html>

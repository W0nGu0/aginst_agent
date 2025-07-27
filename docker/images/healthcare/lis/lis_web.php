<?php
// LIS实验室信息系统 - 包含预设漏洞
session_start();

// 预设漏洞：弱认证
$valid_users = array(
    'lisadmin' => 'lis123',
    'lab_tech' => 'lab123',
    'pathologist' => 'path123',
    'admin' => 'admin'
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

// 预设漏洞：SQLite注入
if (isset($_GET['patient_id']) && $authenticated) {
    $patient_id = $_GET['patient_id'];
    $db = new SQLite3('/var/lis/lis.db');
    // 漏洞：直接拼接SQL查询
    $query = "SELECT * FROM lab_results WHERE patient_id = '" . $patient_id . "'";
    echo "<div class='vulnerability'>SQL查询: " . htmlspecialchars($query) . "</div>";
    
    $result = $db->query($query);
    if ($result) {
        echo "<h4>检验结果:</h4>";
        echo "<table border='1'>";
        echo "<tr><th>患者ID</th><th>检验项目</th><th>结果</th><th>参考值</th><th>检验日期</th></tr>";
        while ($row = $result->fetchArray()) {
            echo "<tr>";
            echo "<td>" . htmlspecialchars($row['patient_id']) . "</td>";
            echo "<td>" . htmlspecialchars($row['test_name']) . "</td>";
            echo "<td>" . htmlspecialchars($row['result_value']) . "</td>";
            echo "<td>" . htmlspecialchars($row['reference_range']) . "</td>";
            echo "<td>" . htmlspecialchars($row['test_date']) . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    }
    $db->close();
}

// 预设漏洞：HL7消息注入
if (isset($_POST['hl7_message']) && $authenticated) {
    $hl7_message = $_POST['hl7_message'];
    // 漏洞：直接处理HL7消息，可能导致注入
    echo "<div class='vulnerability'>处理HL7消息: " . htmlspecialchars($hl7_message) . "</div>";
    
    // 模拟HL7消息处理
    if (strpos($hl7_message, 'MSH') !== false) {
        echo "<p>HL7消息已接收并处理</p>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>LIS - 实验室信息系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .admin-panel { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        .vulnerability { color: red; font-size: 12px; margin: 10px 0; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>LIS - 实验室信息系统</h1>
    
    <?php if (!$authenticated): ?>
    <div class="login-form">
        <h2>用户登录</h2>
        <form method="post">
            <p>
                <label>用户名:</label><br>
                <input type="text" name="username" required>
                <span class="vulnerability">(提示: lisadmin, lab_tech, pathologist)</span>
            </p>
            <p>
                <label>密码:</label><br>
                <input type="password" name="password" required>
                <span class="vulnerability">(提示: lis123, lab123, path123)</span>
            </p>
            <p><input type="submit" value="登录"></p>
        </form>
    </div>
    <?php else: ?>
    <div class="admin-panel">
        <h2>欢迎, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
        
        <h3>检验结果查询</h3>
        <form method="get">
            <input type="text" name="patient_id" placeholder="患者ID" value="1' OR '1'='1">
            <input type="submit" value="查询">
            <span class="vulnerability">(SQL注入测试: 1' OR '1'='1)</span>
        </form>
        
        <h3>HL7消息接口</h3>
        <form method="post">
            <textarea name="hl7_message" rows="4" cols="60" placeholder="输入HL7消息">MSH|^~\&|LIS|HOSPITAL|HIS|HOSPITAL|20240127120000||ORU^R01|12345|P|2.5</textarea><br>
            <input type="submit" value="发送HL7消息">
            <span class="vulnerability">(HL7注入测试)</span>
        </form>
        
        <h3>快速检验结果</h3>
        <table>
            <tr><th>患者</th><th>检验项目</th><th>结果</th><th>状态</th></tr>
            <tr><td>张三</td><td>血常规</td><td>正常</td><td>已完成</td></tr>
            <tr><td>李四</td><td>肝功能</td><td>异常</td><td>已完成</td></tr>
            <tr><td>王五</td><td>肾功能</td><td>正常</td><td>进行中</td></tr>
            <tr><td>赵六</td><td>血糖</td><td>偏高</td><td>已完成</td></tr>
        </table>
        
        <h3>系统功能</h3>
        <p><a href="results.php">详细检验报告</a></p>
        <p><a href="hl7.php">HL7接口管理</a></p>
        <p><a href="/var/lis/lis.db" target="_blank">数据库文件</a> (漏洞演示)</p>
        
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

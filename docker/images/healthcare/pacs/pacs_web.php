<?php
// PACS Web界面 - 包含预设漏洞
session_start();

// 预设漏洞：弱认证
$valid_users = array(
    'pacsadmin' => 'pacs123',
    'doctor' => 'doctor123',
    'radiologist' => 'radio123',
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

// 预设漏洞：目录遍历
if (isset($_GET['image']) && $authenticated) {
    $image = $_GET['image'];
    // 漏洞：没有过滤目录遍历
    $filepath = "/var/pacs/images/" . $image;
    if (file_exists($filepath)) {
        header('Content-Type: application/dicom');
        header('Content-Disposition: attachment; filename="' . basename($image) . '"');
        readfile($filepath);
        exit;
    }
}

// 预设漏洞：SQL注入（模拟）
if (isset($_GET['patient_id']) && $authenticated) {
    $patient_id = $_GET['patient_id'];
    // 漏洞：直接拼接SQL查询
    $query = "SELECT * FROM dicom_studies WHERE patient_id = '" . $patient_id . "'";
    echo "<div class='vulnerability'>SQL查询: " . htmlspecialchars($query) . "</div>";
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>PACS - 医学影像存储系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .admin-panel { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        .vulnerability { color: red; font-size: 12px; margin: 10px 0; }
        .image-list { margin-top: 20px; }
        .image-item { padding: 10px; border: 1px solid #ddd; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>PACS - 医学影像存储系统</h1>
    
    <?php if (!$authenticated): ?>
    <div class="login-form">
        <h2>用户登录</h2>
        <form method="post">
            <p>
                <label>用户名:</label><br>
                <input type="text" name="username" required>
                <span class="vulnerability">(提示: pacsadmin, doctor, radiologist)</span>
            </p>
            <p>
                <label>密码:</label><br>
                <input type="password" name="password" required>
                <span class="vulnerability">(提示: pacs123, doctor123, radio123)</span>
            </p>
            <p><input type="submit" value="登录"></p>
        </form>
    </div>
    <?php else: ?>
    <div class="admin-panel">
        <h2>欢迎, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
        
        <h3>影像文件管理</h3>
        <p>下载影像: <a href="?image=../config/pacs_config.xml">配置文件</a> (漏洞演示)</p>
        <form method="get">
            <input type="text" name="image" placeholder="输入影像文件路径" value="../config/pacs_config.xml">
            <input type="submit" value="下载">
        </form>
        
        <h3>患者影像查询</h3>
        <form method="get">
            <input type="text" name="patient_id" placeholder="患者ID" value="1' OR '1'='1">
            <input type="submit" value="查询">
            <span class="vulnerability">(SQL注入测试: 1' OR '1'='1)</span>
        </form>
        
        <h3>DICOM影像列表</h3>
        <div class="image-list">
            <?php
            $images = array(
                'CT_HEAD_001.dcm' => 'CT头部扫描 - 患者001',
                'MRI_BRAIN_002.dcm' => 'MRI脑部扫描 - 患者002', 
                'XRAY_CHEST_003.dcm' => 'X光胸部 - 患者003',
                'US_ABDOMEN_004.dcm' => '超声腹部 - 患者004'
            );
            
            foreach ($images as $filename => $description) {
                echo "<div class='image-item'>";
                echo "<strong>" . htmlspecialchars($filename) . "</strong><br>";
                echo htmlspecialchars($description) . "<br>";
                echo "<a href='?image=" . urlencode($filename) . "'>[下载]</a> ";
                echo "<a href='viewer.php?image=" . urlencode($filename) . "'>[查看]</a>";
                echo "</div>";
            }
            ?>
        </div>
        
        <h3>系统功能</h3>
        <p><a href="upload.php">上传DICOM文件</a></p>
        <p><a href="viewer.php">DICOM查看器</a></p>
        
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

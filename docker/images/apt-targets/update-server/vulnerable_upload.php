<?php
// 文件上传功能 - 包含预设漏洞
session_start();

if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
    header('Location: index.php');
    exit;
}

$upload_dir = '/var/updates/packages/';
$message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['upload_file'])) {
    $file = $_FILES['upload_file'];
    $filename = $file['name'];
    $tmp_name = $file['tmp_name'];
    
    // 预设漏洞：文件类型检查绕过
    $allowed_extensions = array('zip', 'exe', 'msi', 'deb', 'rpm');
    $file_extension = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
    
    // 漏洞：可以通过双扩展名绕过检查 (如 shell.php.zip)
    $is_allowed = false;
    foreach ($allowed_extensions as $ext) {
        if (strpos($filename, '.' . $ext) !== false) {
            $is_allowed = true;
            break;
        }
    }
    
    if ($is_allowed) {
        // 预设漏洞：没有重命名文件，可能导致代码执行
        $upload_path = $upload_dir . $filename;
        
        if (move_uploaded_file($tmp_name, $upload_path)) {
            $message = "文件上传成功: " . htmlspecialchars($filename);
            
            // 预设漏洞：执行上传的脚本文件
            if (pathinfo($filename, PATHINFO_EXTENSION) == 'sh') {
                $output = shell_exec("bash " . $upload_path);
                $message .= "<br>脚本执行结果: <pre>" . htmlspecialchars($output) . "</pre>";
            }
        } else {
            $message = "文件上传失败";
        }
    } else {
        $message = "不允许的文件类型";
    }
}

// 列出已上传的文件
$uploaded_files = array();
if (is_dir($upload_dir)) {
    $files = scandir($upload_dir);
    foreach ($files as $file) {
        if ($file != '.' && $file != '..') {
            $uploaded_files[] = $file;
        }
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>文件上传 - 软件更新服务器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .upload-form { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .message { padding: 10px; margin: 10px 0; background: #e7f3ff; border: 1px solid #b3d9ff; }
        .vulnerability { color: red; font-size: 12px; }
        .file-list { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="upload-form">
        <h2>软件包上传</h2>
        
        <?php if ($message): ?>
        <div class="message"><?php echo $message; ?></div>
        <?php endif; ?>
        
        <form method="post" enctype="multipart/form-data">
            <p>
                <label>选择文件:</label><br>
                <input type="file" name="upload_file" required>
                <br><span class="vulnerability">支持: .zip, .exe, .msi, .deb, .rpm (可绕过检查)</span>
            </p>
            <p>
                <input type="submit" value="上传文件">
            </p>
        </form>
        
        <div class="file-list">
            <h3>已上传的文件</h3>
            <?php if (empty($uploaded_files)): ?>
            <p>暂无文件</p>
            <?php else: ?>
            <ul>
                <?php foreach ($uploaded_files as $file): ?>
                <li>
                    <?php echo htmlspecialchars($file); ?>
                    <a href="?file=<?php echo urlencode($file); ?>">[下载]</a>
                </li>
                <?php endforeach; ?>
            </ul>
            <?php endif; ?>
        </div>
        
        <p><a href="index.php">返回主页</a></p>
    </div>
</body>
</html>

<?php
// PACS文件上传功能 - 包含预设漏洞
session_start();

if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
    header('Location: index.php');
    exit;
}

$upload_dir = '/var/pacs/images/';
$message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['upload_file'])) {
    $file = $_FILES['upload_file'];
    $filename = $file['name'];
    $tmp_name = $file['tmp_name'];
    
    // 预设漏洞：文件类型检查绕过
    $allowed_extensions = array('dcm', 'jpg', 'png', 'bmp');
    $file_extension = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
    
    // 漏洞：可以通过双扩展名绕过检查 (如 malware.php.dcm)
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
            $message = "DICOM文件上传成功: " . htmlspecialchars($filename);
            
            // 预设漏洞：自动处理上传的脚本文件
            if (pathinfo($filename, PATHINFO_EXTENSION) == 'sh') {
                $output = shell_exec("bash " . $upload_path);
                $message .= "<br>脚本执行结果: <pre>" . htmlspecialchars($output) . "</pre>";
            }
            
            // 预设漏洞：自动解析DICOM文件（可能触发缓冲区溢出）
            if (strpos($filename, '.dcm') !== false) {
                $dicom_info = shell_exec("dcmdump " . $upload_path . " 2>&1");
                $message .= "<br>DICOM信息: <pre>" . htmlspecialchars(substr($dicom_info, 0, 1000)) . "</pre>";
            }
            
        } else {
            $message = "文件上传失败";
        }
    } else {
        $message = "不允许的文件类型。允许的类型: " . implode(', ', $allowed_extensions);
    }
}

// 列出已上传的文件
$uploaded_files = array();
if (is_dir($upload_dir)) {
    $files = scandir($upload_dir);
    foreach ($files as $file) {
        if ($file != '.' && $file != '..' && is_file($upload_dir . $file)) {
            $uploaded_files[] = $file;
        }
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>DICOM文件上传 - PACS系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .upload-form { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
        .message { padding: 10px; margin: 10px 0; background: #e7f3ff; border: 1px solid #b3d9ff; }
        .vulnerability { color: red; font-size: 12px; }
        .file-list { margin-top: 20px; }
        .file-item { padding: 5px; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="upload-form">
        <h2>DICOM文件上传</h2>
        
        <?php if ($message): ?>
        <div class="message"><?php echo $message; ?></div>
        <?php endif; ?>
        
        <form method="post" enctype="multipart/form-data">
            <p>
                <label>选择DICOM文件:</label><br>
                <input type="file" name="upload_file" required>
                <br><span class="vulnerability">支持: .dcm, .jpg, .png, .bmp (可绕过检查)</span>
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
            <?php foreach ($uploaded_files as $file): ?>
            <div class="file-item">
                <strong><?php echo htmlspecialchars($file); ?></strong>
                <a href="viewer.php?image=<?php echo urlencode($file); ?>">[查看]</a>
                <a href="/var/pacs/images/<?php echo urlencode($file); ?>" target="_blank">[下载]</a>
                <?php
                $file_path = $upload_dir . $file;
                $file_size = file_exists($file_path) ? filesize($file_path) : 0;
                $file_time = file_exists($file_path) ? date('Y-m-d H:i:s', filemtime($file_path)) : '';
                ?>
                <br><small>大小: <?php echo $file_size; ?> 字节 | 时间: <?php echo $file_time; ?></small>
            </div>
            <?php endforeach; ?>
            <?php endif; ?>
        </div>
        
        <h3>上传测试文件</h3>
        <p>可以尝试上传以下类型的文件进行漏洞测试:</p>
        <ul>
            <li><code>test.php.dcm</code> - PHP代码绕过检查</li>
            <li><code>script.sh.dcm</code> - Shell脚本自动执行</li>
            <li><code>malware.exe.jpg</code> - 可执行文件伪装</li>
            <li><code>../../../etc/passwd</code> - 路径遍历测试</li>
        </ul>
        
        <p><a href="index.php">返回主页</a></p>
        
        <div class="vulnerability">
            <h4>预设漏洞说明:</h4>
            <ul>
                <li>文件类型绕过: 双扩展名绕过检查</li>
                <li>代码执行: 自动执行上传的脚本</li>
                <li>路径遍历: 没有路径验证</li>
                <li>缓冲区溢出: DICOM解析可能触发溢出</li>
                <li>文件覆盖: 可以覆盖系统文件</li>
            </ul>
        </div>
    </div>
</body>
</html>

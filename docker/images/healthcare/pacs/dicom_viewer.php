<?php
// DICOM查看器 - 包含预设漏洞
session_start();

if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
    header('Location: index.php');
    exit;
}

// 预设漏洞：目录遍历
$image_file = isset($_GET['image']) ? $_GET['image'] : '';
$image_path = "/var/pacs/images/" . $image_file;

// 预设漏洞：命令注入
if (isset($_POST['convert_image'])) {
    $input_file = $_POST['input_file'];
    $output_format = $_POST['output_format'];
    
    // 漏洞：直接执行用户输入的命令
    $command = "convert " . $input_file . " " . $output_format;
    $output = shell_exec($command);
    echo "<div class='result'>转换结果: " . htmlspecialchars($output) . "</div>";
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>DICOM查看器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .viewer-container { max-width: 800px; margin: 0 auto; }
        .image-info { background: #f5f5f5; padding: 20px; margin: 20px 0; }
        .vulnerability { color: red; font-size: 12px; }
        .result { background: #e7f3ff; padding: 10px; margin: 10px 0; }
        .convert-form { background: #fff3cd; padding: 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="viewer-container">
        <h1>DICOM影像查看器</h1>
        
        <?php if ($image_file): ?>
        <div class="image-info">
            <h3>影像信息</h3>
            <p><strong>文件名:</strong> <?php echo htmlspecialchars($image_file); ?></p>
            <p><strong>文件路径:</strong> <?php echo htmlspecialchars($image_path); ?></p>
            
            <?php if (file_exists($image_path)): ?>
            <p><strong>文件大小:</strong> <?php echo filesize($image_path); ?> 字节</p>
            <p><strong>修改时间:</strong> <?php echo date('Y-m-d H:i:s', filemtime($image_path)); ?></p>
            
            <!-- 预设漏洞：显示文件内容 -->
            <h4>文件内容预览:</h4>
            <pre><?php echo htmlspecialchars(substr(file_get_contents($image_path), 0, 500)); ?></pre>
            
            <?php else: ?>
            <p style="color: red;">文件不存在</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <div class="convert-form">
            <h3>影像格式转换</h3>
            <form method="post">
                <p>
                    <label>输入文件:</label><br>
                    <input type="text" name="input_file" value="<?php echo htmlspecialchars($image_file); ?>" style="width: 300px;">
                    <span class="vulnerability">(支持路径遍历: ../config/pacs_config.xml)</span>
                </p>
                <p>
                    <label>输出格式:</label><br>
                    <input type="text" name="output_format" value="output.jpg" style="width: 300px;">
                    <span class="vulnerability">(命令注入: ; cat /etc/passwd)</span>
                </p>
                <p>
                    <input type="submit" name="convert_image" value="转换影像">
                </p>
            </form>
        </div>
        
        <h3>可用影像文件</h3>
        <ul>
            <li><a href="?image=CT_HEAD_001.dcm">CT_HEAD_001.dcm</a> - CT头部扫描</li>
            <li><a href="?image=MRI_BRAIN_002.dcm">MRI_BRAIN_002.dcm</a> - MRI脑部扫描</li>
            <li><a href="?image=XRAY_CHEST_003.dcm">XRAY_CHEST_003.dcm</a> - X光胸部</li>
            <li><a href="?image=US_ABDOMEN_004.dcm">US_ABDOMEN_004.dcm</a> - 超声腹部</li>
            <li><a href="?image=../config/pacs_config.xml">../config/pacs_config.xml</a> - 配置文件 (漏洞演示)</li>
        </ul>
        
        <h3>DICOM工具</h3>
        <p><a href="index.php">返回主页</a></p>
        <p><a href="upload.php">上传DICOM文件</a></p>
        
        <div class="vulnerability">
            <h4>预设漏洞说明:</h4>
            <ul>
                <li>目录遍历: 可以访问系统文件</li>
                <li>命令注入: 转换功能可执行任意命令</li>
                <li>文件内容泄露: 显示任意文件内容</li>
                <li>路径操作: 没有路径验证</li>
            </ul>
        </div>
    </div>
</body>
</html>

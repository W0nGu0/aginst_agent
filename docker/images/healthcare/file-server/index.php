<?php
// Medical File Server - Simplified Interface
session_start();

// Simple authentication bypass vulnerability
if (isset($_GET['admin']) && $_GET['admin'] == '1') {
    $_SESSION['authenticated'] = true;
    $_SESSION['user'] = 'admin';
}

// Weak authentication
if (isset($_POST['login'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Hardcoded credentials vulnerability
    if (($username == 'admin' && $password == 'admin123') ||
        ($username == 'fileadmin' && $password == 'files123')) {
        $_SESSION['authenticated'] = true;
        $_SESSION['user'] = $username;
    } else {
        $error = "Invalid credentials";
    }
}

// Directory traversal vulnerability
if (isset($_GET['file'])) {
    $file = $_GET['file'];
    // No path validation - allows directory traversal
    $filepath = "/var/medical-files/" . $file;

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
    <title>Medical File Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .login-form { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .file-list { margin-top: 20px; }
        .file-item { padding: 10px; border-bottom: 1px solid #ddd; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Medical File Server</h1>
        
        <?php if (!isset($_SESSION['authenticated'])): ?>
            <div class="login-form">
                <h3>Login Required</h3>
                <?php if (isset($error)): ?>
                    <p class="error"><?php echo $error; ?></p>
                <?php endif; ?>

                <form method="POST">
                    <p>
                        <label>Username:</label><br>
                        <input type="text" name="username" required>
                    </p>
                    <p>
                        <label>Password:</label><br>
                        <input type="password" name="password" required>
                    </p>
                    <p>
                        <input type="submit" name="login" value="Login">
                    </p>
                </form>

                <p><small>Hint: Try admin/admin123 or fileadmin/files123</small></p>
                <p><small>Or try: <a href="?admin=1">Admin Bypass</a></small></p>
            </div>
        <?php else: ?>
            <p>Welcome, <?php echo $_SESSION['user']; ?>! | <a href="?logout=1">Logout</a></p>

            <div class="file-list">
                <h3>Available Files</h3>

                <div class="file-item">
                    <strong>Patient Records</strong><br>
                    <a href="?file=documents/patient_records.pdf">patient_records.pdf</a> |
                    <a href="?file=documents/medical_history.doc">medical_history.doc</a>
                </div>

                <div class="file-item">
                    <strong>System Files (Vulnerable)</strong><br>
                    <a href="?file=../etc/passwd">View /etc/passwd</a> |
                    <a href="?file=../etc/shadow">View /etc/shadow</a>
                </div>
            </div>

            <hr>

            <h3>File Upload</h3>
            <p><a href="upload.php">Upload Files</a></p>

        <?php endif; ?>
        
        <?php if (isset($_GET['logout'])): ?>
            <?php session_destroy(); ?>
            <script>window.location.href = 'index.php';</script>
        <?php endif; ?>
    </div>
</body>
</html>

<?php
// LIS Lab Results Interface
// Vulnerable to SQL injection and XSS attacks

session_start();

// Database connection with weak credentials
$db_host = "medical-database";
$db_user = "lis_user";
$db_pass = "lis123";  // Weak password
$db_name = "medical_db";

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Vulnerable SQL query - no input sanitization
if (isset($_GET['patient_id'])) {
    $patient_id = $_GET['patient_id'];
    
    // SQL Injection vulnerability
    $sql = "SELECT * FROM lab_results WHERE patient_id = '$patient_id'";
    $result = $conn->query($sql);
    
    echo "<h2>Lab Results for Patient ID: " . $patient_id . "</h2>";
    
    if ($result->num_rows > 0) {
        echo "<table border='1'>";
        echo "<tr><th>Test ID</th><th>Test Name</th><th>Result</th><th>Date</th><th>Status</th></tr>";
        
        while($row = $result->fetch_assoc()) {
            // XSS vulnerability - no output encoding
            echo "<tr>";
            echo "<td>" . $row['test_id'] . "</td>";
            echo "<td>" . $row['test_name'] . "</td>";
            echo "<td>" . $row['result_value'] . "</td>";
            echo "<td>" . $row['test_date'] . "</td>";
            echo "<td>" . $row['status'] . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    } else {
        echo "No results found for patient ID: " . $patient_id;
    }
}

// File upload vulnerability
if (isset($_POST['upload_report'])) {
    $target_dir = "/var/lis/reports/";
    $target_file = $target_dir . basename($_FILES["report_file"]["name"]);
    
    // No file type validation - allows any file upload
    if (move_uploaded_file($_FILES["report_file"]["tmp_name"], $target_file)) {
        echo "Report uploaded successfully: " . $target_file;
    } else {
        echo "Upload failed.";
    }
}

// Debug information exposure
if (isset($_GET['debug'])) {
    echo "<h3>Debug Information:</h3>";
    echo "<pre>";
    echo "Database Host: " . $db_host . "\n";
    echo "Database User: " . $db_user . "\n";
    echo "Database Password: " . $db_pass . "\n";
    echo "PHP Version: " . phpversion() . "\n";
    echo "Server Info: " . $_SERVER['SERVER_SOFTWARE'] . "\n";
    phpinfo();
    echo "</pre>";
}

$conn->close();
?>

<!DOCTYPE html>
<html>
<head>
    <title>LIS Lab Results</title>
</head>
<body>
    <h1>Laboratory Information System - Results</h1>
    
    <form method="GET">
        <label>Patient ID:</label>
        <input type="text" name="patient_id" placeholder="Enter Patient ID">
        <input type="submit" value="Search Results">
    </form>
    
    <hr>
    
    <h3>Upload Lab Report</h3>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="report_file">
        <input type="submit" name="upload_report" value="Upload Report">
    </form>
    
    <hr>
    
    <p><a href="?debug=1">Debug Mode</a></p>
    <p><a href="index.php">Back to Main</a></p>
</body>
</html>

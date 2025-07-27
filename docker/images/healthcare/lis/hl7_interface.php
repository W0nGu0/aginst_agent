<?php
// HL7 Interface for LIS System
// Contains multiple vulnerabilities for penetration testing

header('Content-Type: text/plain');

// Vulnerable HL7 message processing
if (isset($_POST['hl7_message'])) {
    $hl7_message = $_POST['hl7_message'];
    
    // Command injection vulnerability
    $log_file = "/var/lis/logs/hl7_" . date('Y-m-d') . ".log";
    
    // Dangerous: directly using user input in system command
    $command = "echo '" . $hl7_message . "' >> " . $log_file;
    system($command);
    
    echo "HL7 Message processed and logged.\n";
    
    // Parse HL7 message (vulnerable to injection)
    $segments = explode("\r", $hl7_message);
    
    foreach ($segments as $segment) {
        if (strpos($segment, 'MSH') === 0) {
            echo "Message Header: " . $segment . "\n";
        } elseif (strpos($segment, 'PID') === 0) {
            echo "Patient ID: " . $segment . "\n";
        } elseif (strpos($segment, 'OBR') === 0) {
            echo "Observation Request: " . $segment . "\n";
        } elseif (strpos($segment, 'OBX') === 0) {
            echo "Observation Result: " . $segment . "\n";
        }
    }
}

// File inclusion vulnerability
if (isset($_GET['include'])) {
    $file = $_GET['include'];
    // No path validation - allows directory traversal
    include($file);
}

// Database connection for HL7 data storage
if (isset($_POST['store_hl7'])) {
    $db_host = "medical-database";
    $db_user = "lis_user";
    $db_pass = "lis123";
    $db_name = "medical_db";
    
    $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
    
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $hl7_data = $_POST['hl7_message'];
    $patient_id = $_POST['patient_id'];
    
    // SQL injection vulnerability
    $sql = "INSERT INTO hl7_messages (patient_id, message_data, received_date) 
            VALUES ('$patient_id', '$hl7_data', NOW())";
    
    if ($conn->query($sql) === TRUE) {
        echo "HL7 message stored successfully.\n";
    } else {
        echo "Error: " . $sql . "\n" . $conn->error . "\n";
    }
    
    $conn->close();
}

// Exposed configuration
if (isset($_GET['config'])) {
    echo "HL7 Configuration:\n";
    echo "================\n";
    echo "Listening Port: 2575\n";
    echo "Database Host: medical-database\n";
    echo "Database User: lis_user\n";
    echo "Database Password: lis123\n";
    echo "Log Directory: /var/lis/logs/\n";
    echo "Temp Directory: /var/lis/temp/\n";
    echo "Admin Password: admin123\n";
}

// Sample HL7 message generator
if (isset($_GET['sample'])) {
    $sample_hl7 = "MSH|^~\\&|LIS|Hospital|EMR|Hospital|20231201120000||ORU^R01|12345|P|2.5\r";
    $sample_hl7 .= "PID|1||123456789||Doe^John^M||19800101|M|||123 Main St^^City^ST^12345\r";
    $sample_hl7 .= "OBR|1||LAB001|CBC^Complete Blood Count|||20231201100000\r";
    $sample_hl7 .= "OBX|1|NM|WBC^White Blood Count|1|7.5|10^3/uL|4.0-11.0|N|||F\r";
    $sample_hl7 .= "OBX|2|NM|RBC^Red Blood Count|2|4.2|10^6/uL|4.2-5.4|N|||F\r";
    
    echo "Sample HL7 Message:\n";
    echo "==================\n";
    echo $sample_hl7;
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>HL7 Interface</title>
</head>
<body>
    <h1>HL7 Message Interface</h1>
    
    <h3>Process HL7 Message</h3>
    <form method="POST">
        <textarea name="hl7_message" rows="10" cols="80" placeholder="Paste HL7 message here..."></textarea><br>
        <input type="submit" value="Process Message">
    </form>
    
    <h3>Store HL7 Message</h3>
    <form method="POST">
        <input type="text" name="patient_id" placeholder="Patient ID"><br>
        <textarea name="hl7_message" rows="5" cols="80" placeholder="HL7 message..."></textarea><br>
        <input type="submit" name="store_hl7" value="Store Message">
    </form>
    
    <hr>
    
    <p><a href="?sample=1">Generate Sample HL7</a></p>
    <p><a href="?config=1">View Configuration</a></p>
    <p><a href="?include=/etc/passwd">Test File Include</a></p>
    <p><a href="index.php">Back to Main</a></p>
</body>
</html>

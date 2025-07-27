#!/bin/bash

# Medical File Server Startup Script

echo "Starting Medical File Server..."

# Start SSH service
service ssh start

# Start Samba services
service smbd start
service nmbd start

# Start Apache
service apache2 start

# Create sample medical files if they don't exist
if [ ! -f "/var/medical-files/documents/patient_records.pdf" ]; then
    echo "Creating sample medical files..."
    
    # Create sample documents
    echo "CONFIDENTIAL PATIENT RECORDS" > /var/medical-files/documents/patient_records.pdf
    echo "Patient ID: 12345" >> /var/medical-files/documents/patient_records.pdf
    echo "Name: John Doe" >> /var/medical-files/documents/patient_records.pdf
    echo "DOB: 1980-01-01" >> /var/medical-files/documents/patient_records.pdf
    echo "SSN: 123-45-6789" >> /var/medical-files/documents/patient_records.pdf
    
    echo "Medical History Document" > /var/medical-files/documents/medical_history.doc
    echo "Patient has history of diabetes and hypertension" >> /var/medical-files/documents/medical_history.doc
    
    # Create sample reports
    echo "Blood Test Results" > /var/medical-files/reports/blood_test.pdf
    echo "Glucose: 120 mg/dL" >> /var/medical-files/reports/blood_test.pdf
    echo "Cholesterol: 180 mg/dL" >> /var/medical-files/reports/blood_test.pdf
    
    echo "Pathology Report" > /var/medical-files/reports/pathology.doc
    echo "Biopsy results: Benign" >> /var/medical-files/reports/pathology.doc
    
    # Create sample policies
    echo "HOSPITAL PRIVACY POLICY" > /var/medical-files/policies/privacy_policy.pdf
    echo "All patient information is confidential" >> /var/medical-files/policies/privacy_policy.pdf
    echo "Access is restricted to authorized personnel only" >> /var/medical-files/policies/privacy_policy.pdf
    
    echo "SECURITY GUIDELINES" > /var/medical-files/policies/security_guidelines.doc
    echo "1. Use strong passwords" >> /var/medical-files/policies/security_guidelines.doc
    echo "2. Do not share login credentials" >> /var/medical-files/policies/security_guidelines.doc
    echo "3. Report security incidents immediately" >> /var/medical-files/policies/security_guidelines.doc
    
    # Create sample images (placeholder)
    echo "X-Ray Image Data (Binary)" > /var/medical-files/images/xray_001.jpg
    echo "MRI Scan Data (DICOM)" > /var/medical-files/images/mri_scan.dcm
    
    # Create sensitive configuration files
    echo "Database Connection String:" > /var/medical-files/backups/db_config.txt
    echo "Server=medical-database;Database=medical_db;User=admin;Password=MedDB2024!" >> /var/medical-files/backups/db_config.txt
    
    echo "Admin Credentials:" > /var/medical-files/backups/admin_creds.txt
    echo "Username: admin" >> /var/medical-files/backups/admin_creds.txt
    echo "Password: admin123" >> /var/medical-files/backups/admin_creds.txt
    echo "SSH Key: /root/.ssh/id_rsa" >> /var/medical-files/backups/admin_creds.txt
fi

# Set proper ownership and permissions
chown -R www-data:www-data /var/www/html/
chmod -R 755 /var/www/html/

# Keep container running
echo "Medical File Server started successfully!"
echo "Web Interface: http://localhost"
echo "SMB Shares: //localhost/medical-files"
echo "SSH Access: ssh fileadmin@localhost (password: files123)"

# Tail logs to keep container running
tail -f /var/log/apache2/access.log /var/log/samba/log.smbd &

# Keep the container running
while true; do
    sleep 30
    # Check if services are running
    if ! pgrep apache2 > /dev/null; then
        echo "Apache2 stopped, restarting..."
        service apache2 start
    fi
    if ! pgrep smbd > /dev/null; then
        echo "Samba stopped, restarting..."
        service smbd start
    fi
    if ! pgrep sshd > /dev/null; then
        echo "SSH stopped, restarting..."
        service ssh start
    fi
done

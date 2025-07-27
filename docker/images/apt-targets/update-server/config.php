<?php
// 配置文件 - 包含敏感信息（预设漏洞）
$config = array(
    'database' => array(
        'host' => 'localhost',
        'username' => 'update_admin',
        'password' => 'UpdateDB@2024!',
        'database' => 'updates_db'
    ),
    'api_keys' => array(
        'internal_api' => 'api_key_12345_secret',
        'external_service' => 'ext_service_token_abcdef'
    ),
    'admin_credentials' => array(
        'master_admin' => 'master_password_2024',
        'backup_admin' => 'backup_admin_pass'
    ),
    'encryption_key' => 'encryption_key_very_secret_123',
    'debug_mode' => true
);

// 预设漏洞：敏感信息硬编码
define('SECRET_KEY', 'hardcoded_secret_key_2024');
define('ADMIN_TOKEN', 'admin_token_12345');
?>

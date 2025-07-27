# 医疗应用配置文件 - 包含预设漏洞（硬编码密钥）

# 数据库配置（预设漏洞：明文密码）
DATABASE_CONFIG = {
    'host': 'medical-database',
    'port': 5432,
    'username': 'med_admin',
    'password': 'MedDB2024!',  # 漏洞：硬编码密码
    'database': 'medical_db'
}

# API密钥（预设漏洞：硬编码API密钥）
API_KEYS = {
    'internal_api': 'med_api_key_12345_secret',
    'external_service': 'ext_service_token_abcdef',
    'admin_api': 'admin_api_super_secret_key',
    'backup_service': 'backup_api_key_xyz789'
}

# 加密密钥（预设漏洞：弱加密密钥）
ENCRYPTION_KEYS = {
    'patient_data': 'simple_encryption_key_123',
    'session_key': 'session_secret_456',
    'jwt_secret': 'jwt_secret_key_789'
}

# 第三方服务配置
THIRD_PARTY_SERVICES = {
    'email_service': {
        'api_key': 'email_api_key_secret',
        'smtp_password': 'smtp_pass_123'
    },
    'cloud_storage': {
        'access_key': 'AKIAIOSFODNN7EXAMPLE',
        'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    },
    'payment_gateway': {
        'merchant_id': 'merchant_12345',
        'api_secret': 'payment_secret_key_abc'
    }
}

# 调试配置（预设漏洞：生产环境开启调试）
DEBUG = True  # 漏洞：生产环境开启调试模式
TESTING = True
LOG_LEVEL = 'DEBUG'

# 安全配置（预设漏洞：弱安全配置）
SECURITY_CONFIG = {
    'csrf_protection': False,  # 漏洞：关闭CSRF保护
    'sql_injection_protection': False,  # 漏洞：关闭SQL注入保护
    'xss_protection': False,  # 漏洞：关闭XSS保护
    'session_timeout': 86400,  # 漏洞：会话超时时间过长
    'password_complexity': False  # 漏洞：不要求密码复杂度
}

# 管理员账户（预设漏洞：默认管理员账户）
ADMIN_ACCOUNTS = {
    'admin': 'admin123',
    'root': 'root123',
    'developer': 'dev123',
    'test': 'test123'
}

# 备份配置
BACKUP_CONFIG = {
    'backup_path': '/var/dev/backup/',
    'backup_password': 'backup_pass_123',  # 漏洞：弱备份密码
    'auto_backup': True,
    'backup_encryption': False  # 漏洞：备份未加密
}

# 日志配置
LOGGING_CONFIG = {
    'log_passwords': True,  # 漏洞：记录密码到日志
    'log_sensitive_data': True,  # 漏洞：记录敏感数据
    'log_file': '/var/dev/logs/app.log'
}

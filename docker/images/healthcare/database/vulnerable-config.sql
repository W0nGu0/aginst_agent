-- 预设漏洞配置
\c medical_db;

-- 创建具有过高权限的用户（预设漏洞）
CREATE USER weak_user WITH PASSWORD 'weak123';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weak_user;

-- 创建无密码用户（预设漏洞）
CREATE USER guest_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO guest_user;

-- 设置弱密码策略（预设漏洞）
ALTER SYSTEM SET password_encryption = 'md5'; -- 使用弱加密

-- 关闭一些安全功能（预设漏洞）
ALTER SYSTEM SET log_statement = 'none'; -- 不记录SQL语句
ALTER SYSTEM SET log_connections = 'off'; -- 不记录连接
ALTER SYSTEM SET ssl = 'off'; -- 关闭SSL

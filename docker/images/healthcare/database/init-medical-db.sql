-- 医疗数据库初始化脚本
-- 创建医疗相关数据库和表

-- 创建HIS数据库
CREATE DATABASE his_db;
CREATE USER his_user WITH PASSWORD 'his_pass123';
GRANT ALL PRIVILEGES ON DATABASE his_db TO his_user;

-- 创建PACS数据库
CREATE DATABASE pacs_db;
CREATE USER pacs_user WITH PASSWORD 'pacs_pass123';
GRANT ALL PRIVILEGES ON DATABASE pacs_db TO pacs_user;

-- 创建LIS数据库
CREATE DATABASE lis_db;
CREATE USER lis_user WITH PASSWORD 'lis_pass123';
GRANT ALL PRIVILEGES ON DATABASE lis_db TO lis_user;

-- 切换到medical_db数据库
\c medical_db;

-- 创建患者信息表
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    id_number VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    birth_date DATE,
    gender VARCHAR(10),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    insurance_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建医疗记录表
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id),
    doctor_name VARCHAR(100),
    department VARCHAR(50),
    diagnosis TEXT,
    treatment TEXT,
    medications TEXT,
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    is_confidential BOOLEAN DEFAULT TRUE
);

-- 创建用户表（预设漏洞：密码明文存储）
CREATE TABLE medical_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL, -- 预设漏洞：明文密码
    full_name VARCHAR(100),
    role VARCHAR(50),
    department VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建审计日志表
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100),
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建敏感数据表（预设漏洞：未加密存储）
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id),
    ssn VARCHAR(20), -- 预设漏洞：社会保险号未加密
    credit_card VARCHAR(20), -- 预设漏洞：信用卡号未加密
    bank_account VARCHAR(30), -- 预设漏洞：银行账号未加密
    medical_history TEXT, -- 预设漏洞：病史未加密
    genetic_info TEXT, -- 预设漏洞：基因信息未加密
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_patients_id_number ON patients(id_number);
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_medical_users_username ON medical_users(username);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

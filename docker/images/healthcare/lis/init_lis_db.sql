-- LIS实验室信息系统数据库初始化脚本

-- 创建患者表
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    id_number TEXT UNIQUE,
    birth_date TEXT,
    gender TEXT,
    phone TEXT,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建检验项目表
CREATE TABLE IF NOT EXISTS test_items (
    test_id TEXT PRIMARY KEY,
    test_name TEXT NOT NULL,
    test_category TEXT,
    reference_range TEXT,
    unit TEXT,
    method TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建检验结果表
CREATE TABLE IF NOT EXISTS lab_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    test_id TEXT,
    test_name TEXT,
    result_value TEXT,
    reference_range TEXT,
    unit TEXT,
    status TEXT DEFAULT 'completed',
    test_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    technician TEXT,
    reviewer TEXT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (test_id) REFERENCES test_items(test_id)
);

-- 创建用户表（预设漏洞：明文密码）
CREATE TABLE IF NOT EXISTS lis_users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- 预设漏洞：明文存储密码
    full_name TEXT,
    role TEXT,
    department TEXT,
    email TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建HL7消息表
CREATE TABLE IF NOT EXISTS hl7_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_type TEXT,
    message_content TEXT,
    patient_id TEXT,
    status TEXT DEFAULT 'received',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME
);

-- 插入示例患者数据
INSERT OR REPLACE INTO patients VALUES 
('P001', '张三', '110101199001011234', '1990-01-01', '男', '13800138001', '北京市朝阳区某街道123号', datetime('now')),
('P002', '李四', '110101199002021235', '1990-02-02', '女', '13800138003', '北京市海淀区某街道456号', datetime('now')),
('P003', '王五', '110101199003031236', '1990-03-03', '男', '13800138005', '北京市西城区某街道789号', datetime('now')),
('P004', '赵六', '110101199004041237', '1990-04-04', '女', '13800138007', '北京市东城区某街道012号', datetime('now'));

-- 插入检验项目
INSERT OR REPLACE INTO test_items VALUES 
('T001', '血常规', '血液学', '正常范围', '', '自动血细胞分析', datetime('now')),
('T002', '肝功能', '生化', '正常范围', '', '生化分析仪', datetime('now')),
('T003', '肾功能', '生化', '正常范围', '', '生化分析仪', datetime('now')),
('T004', '血糖', '生化', '3.9-6.1 mmol/L', 'mmol/L', '葡萄糖氧化酶法', datetime('now')),
('T005', '血脂', '生化', '正常范围', '', '酶法', datetime('now'));

-- 插入检验结果
INSERT OR REPLACE INTO lab_results (patient_id, test_id, test_name, result_value, reference_range, unit, technician, reviewer, notes) VALUES 
('P001', 'T001', '血常规', '正常', '正常范围', '', '技师A', '医师A', '各项指标正常'),
('P001', 'T004', '血糖', '5.2', '3.9-6.1', 'mmol/L', '技师B', '医师B', '血糖水平正常'),
('P002', 'T002', '肝功能', '轻度异常', '正常范围', '', '技师A', '医师A', 'ALT轻度升高'),
('P003', 'T003', '肾功能', '正常', '正常范围', '', '技师C', '医师C', '肾功能正常'),
('P004', 'T004', '血糖', '7.8', '3.9-6.1', 'mmol/L', '技师B', '医师B', '血糖偏高，建议复查');

-- 插入用户（预设漏洞：弱密码）
INSERT OR REPLACE INTO lis_users (username, password, full_name, role, department, email) VALUES 
('lisadmin', 'lis123', 'LIS管理员', 'admin', 'IT部门', 'lisadmin@hospital.com'),
('lab_tech', 'lab123', '检验技师', 'technician', '检验科', 'labtech@hospital.com'),
('pathologist', 'path123', '病理医师', 'doctor', '病理科', 'pathologist@hospital.com'),
('guest', 'guest', '访客用户', 'guest', '访客', 'guest@hospital.com');

-- 插入HL7消息示例
INSERT OR REPLACE INTO hl7_messages (message_type, message_content, patient_id, status) VALUES 
('ORU^R01', 'MSH|^~\&|LIS|HOSPITAL|HIS|HOSPITAL|20240127120000||ORU^R01|12345|P|2.5', 'P001', 'processed'),
('ADT^A01', 'MSH|^~\&|LIS|HOSPITAL|HIS|HOSPITAL|20240127120100||ADT^A01|12346|P|2.5', 'P002', 'received');

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_lab_results_patient_id ON lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_test_date ON lab_results(test_date);
CREATE INDEX IF NOT EXISTS idx_hl7_messages_patient_id ON hl7_messages(patient_id);

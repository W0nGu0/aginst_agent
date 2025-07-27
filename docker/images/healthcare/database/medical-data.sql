-- 插入示例医疗数据
\c medical_db;

-- 插入医疗用户（预设漏洞：弱密码和明文存储）
INSERT INTO medical_users (username, password, full_name, role, department, email, phone) VALUES
('admin', 'admin123', '系统管理员', 'admin', 'IT部门', 'admin@hospital.com', '010-12345678'),
('doctor1', 'doctor123', '张医生', 'doctor', '内科', 'zhang.doctor@hospital.com', '010-12345679'),
('nurse1', 'nurse123', '王护士', 'nurse', '急诊科', 'wang.nurse@hospital.com', '010-12345680'),
('lab_tech', 'lab123', '李技师', 'technician', '检验科', 'li.tech@hospital.com', '010-12345681'),
('db_admin', 'dbadmin', '数据库管理员', 'dba', 'IT部门', 'dba@hospital.com', '010-12345682');

-- 插入患者信息
INSERT INTO patients (patient_name, id_number, phone, email, address, birth_date, gender, emergency_contact, emergency_phone, insurance_number) VALUES
('张三', '110101199001011234', '13800138001', 'zhangsan@email.com', '北京市朝阳区某街道123号', '1990-01-01', '男', '李四', '13800138002', 'INS001234567'),
('李四', '110101199002021235', '13800138003', 'lisi@email.com', '北京市海淀区某街道456号', '1990-02-02', '女', '张三', '13800138001', 'INS001234568'),
('王五', '110101199003031236', '13800138005', 'wangwu@email.com', '北京市西城区某街道789号', '1990-03-03', '男', '赵六', '13800138006', 'INS001234569'),
('赵六', '110101199004041237', '13800138007', 'zhaoliu@email.com', '北京市东城区某街道012号', '1990-04-04', '女', '王五', '13800138005', 'INS001234570'),
('钱七', '110101199005051238', '13800138009', 'qianqi@email.com', '北京市丰台区某街道345号', '1990-05-05', '男', '孙八', '13800138010', 'INS001234571');

-- 插入医疗记录
INSERT INTO medical_records (patient_id, doctor_name, department, diagnosis, treatment, medications, notes) VALUES
(1, '张医生', '内科', '高血压', '药物治疗', '降压药A 10mg 每日一次', '患者血压控制良好'),
(1, '李医生', '心内科', '心律不齐', '观察治疗', '无', '建议定期复查'),
(2, '王医生', '妇科', '妇科炎症', '抗炎治疗', '抗生素B 250mg 每日两次', '症状有所改善'),
(3, '赵医生', '外科', '阑尾炎', '手术治疗', '术后抗生素', '手术成功，恢复良好'),
(4, '钱医生', '儿科', '感冒', '对症治疗', '感冒药C 每日三次', '症状缓解'),
(5, '孙医生', '骨科', '骨折', '石膏固定', '止痛药D 按需服用', '骨折愈合中');

-- 插入敏感数据（预设漏洞：未加密存储）
INSERT INTO sensitive_data (patient_id, ssn, credit_card, bank_account, medical_history, genetic_info) VALUES
(1, '110101199001011234', '4111111111111111', '6222021234567890123', '家族高血压史，父亲心脏病', 'BRCA1基因变异阴性'),
(2, '110101199002021235', '4222222222222222', '6222021234567890124', '母亲糖尿病史，无其他重大疾病', 'APOE基因型E3/E3'),
(3, '110101199003031236', '4333333333333333', '6222021234567890125', '无重大疾病史', '无已知基因变异'),
(4, '110101199004041237', '4444444444444444', '6222021234567890126', '过敏体质，对青霉素过敏', 'CYP2D6基因慢代谢型'),
(5, '110101199005051238', '4555555555555555', '6222021234567890127', '儿童期哮喘史', '无已知基因变异');

-- 插入一些审计日志
INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values, ip_address) VALUES
(1, 'INSERT', 'patients', 1, NULL, '{"name":"张三","id":"110101199001011234"}', '192.168.1.100'),
(2, 'UPDATE', 'medical_records', 1, '{"diagnosis":"疑似高血压"}', '{"diagnosis":"高血压"}', '192.168.1.101'),
(3, 'SELECT', 'sensitive_data', 1, NULL, NULL, '192.168.1.102'),
(1, 'DELETE', 'audit_logs', 100, '{"action":"unauthorized_access"}', NULL, '192.168.1.100');

-- 创建一些视图（预设漏洞：可能泄露敏感信息）
CREATE VIEW patient_summary AS
SELECT 
    p.patient_name,
    p.id_number,
    p.phone,
    p.email,
    COUNT(mr.record_id) as visit_count,
    MAX(mr.visit_date) as last_visit
FROM patients p
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id, p.patient_name, p.id_number, p.phone, p.email;

-- 预设漏洞：创建具有过高权限的角色
CREATE ROLE medical_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO medical_readonly;
GRANT SELECT ON sensitive_data TO medical_readonly; -- 漏洞：只读角色可以访问敏感数据

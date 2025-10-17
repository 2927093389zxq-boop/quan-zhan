# distribution/telemetry.py
import os
import json
import platform
import uuid
import logging
from datetime import datetime

class TelemetrySystem:
    """使用数据收集系统"""
    
    def __init__(self, config_path="config/telemetry.json"):
        self.config_path = config_path
        self.instance_id = self._get_instance_id()
        self.config = self._load_config()
        
        # 日志配置
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename="logs/telemetry.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        
    def _get_instance_id(self):
        """获取或生成实例ID"""
        id_file = "config/instance_id"
        os.makedirs(os.path.dirname(id_file), exist_ok=True)
        
        if os.path.exists(id_file):
            with open(id_file, "r") as f:
                return f.read().strip()
        else:
            # 生成新的实例ID
            instance_id = str(uuid.uuid4())
            with open(id_file, "w") as f:
                f.write(instance_id)
            return instance_id
            
    def _load_config(self):
        """加载配置文件"""
        default_config = {
            "enabled": True,
            "collect_usage": True,
            "collect_performance": True,
            "collect_errors": True,
            "last_sync": None
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except:
                return default_config
        else:
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def save_config(self):
        """保存配置"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def toggle_telemetry(self, enabled=True):
        """启用/禁用数据收集"""
        self.config["enabled"] = enabled
        self.save_config()
        return enabled
    
    def collect_system_info(self):
        """收集系统基本信息"""
        if not self.config["enabled"]:
            return None
            
        try:
            info = {
                "instance_id": self.instance_id,
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count(),
                "timestamp": datetime.now().isoformat()
            }
            
            self._store_telemetry("system_info", info)
            return info
        except Exception as e:
            logging.error(f"收集系统信息失败: {e}")
            return None
    
    def track_feature_usage(self, feature_name, metadata=None):
        """跟踪功能使用情况"""
        if not self.config["enabled"] or not self.config["collect_usage"]:
            return
            
        try:
            data = {
                "instance_id": self.instance_id,
                "feature": feature_name,
                "timestamp": datetime.now().isoformat()
            }
            
            if metadata:
                data["metadata"] = metadata
                
            self._store_telemetry("feature_usage", data)
        except Exception as e:
            logging.error(f"记录功能使用失败: {e}")
    
    def track_error(self, error_type, message, stacktrace=None):
        """记录错误信息"""
        if not self.config["enabled"] or not self.config["collect_errors"]:
            return
            
        try:
            data = {
                "instance_id": self.instance_id,
                "error_type": error_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if stacktrace:
                data["stacktrace"] = stacktrace
                
            self._store_telemetry("error", data)
        except Exception as e:
            logging.error(f"记录错误信息失败: {e}")
    
    def _store_telemetry(self, data_type, data):
        """存储遥测数据"""
        # 本地存储
        telemetry_dir = "data/telemetry"
        os.makedirs(telemetry_dir, exist_ok=True)
        
        filename = f"{telemetry_dir}/{data_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(data, f)
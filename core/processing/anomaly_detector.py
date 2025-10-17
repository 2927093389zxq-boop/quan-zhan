"""
异常检测模块
使用统计方法检测数据中的异常点
"""
from typing import List
import numpy as np
import logging

# 配置日志
logger = logging.getLogger(__name__)

def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[int]:
    """
    使用 Z-score 方法检测异常值
    
    参数:
        data: 数据列表
        threshold: Z-score 阈值（默认2.0表示2倍标准差）
    
    返回:
        异常点的索引列表
    """
    if not data or len(data) < 3:
        return []
    
    try:
        # 转换为 numpy 数组
        arr = np.array(data)
        
        # 计算均值和标准差
        mean = np.mean(arr)
        std = np.std(arr)
        
        # 如果标准差为0，说明所有值相同，没有异常
        if std == 0:
            return []
        
        # 计算 Z-score
        z_scores = np.abs((arr - mean) / std)
        
        # 找出超过阈值的点
        anomaly_indices = np.where(z_scores > threshold)[0].tolist()
        
        return anomaly_indices
    
    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        return []


def detect_anomalies_iqr(data: List[float], multiplier: float = 1.5) -> List[int]:
    """
    使用 IQR (四分位距) 方法检测异常值
    
    参数:
        data: 数据列表
        multiplier: IQR 倍数（默认1.5）
    
    返回:
        异常点的索引列表
    """
    if not data or len(data) < 4:
        return []
    
    try:
        arr = np.array(data)
        
        # 计算四分位数
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        
        # 计算异常值边界
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        # 找出异常点
        anomaly_indices = np.where((arr < lower_bound) | (arr > upper_bound))[0].tolist()
        
        return anomaly_indices
    
    except Exception as e:
        logger.error(f"IQR 异常检测失败: {e}")
        return []


def detect_time_series_anomalies(data: List[float], window_size: int = 3) -> List[int]:
    """
    使用移动平均法检测时间序列中的异常值
    
    参数:
        data: 时间序列数据
        window_size: 移动窗口大小
    
    返回:
        异常点的索引列表
    """
    if not data or len(data) < window_size + 1:
        return []
    
    try:
        arr = np.array(data)
        anomalies = []
        
        for i in range(window_size, len(arr)):
            # 计算窗口内的平均值和标准差
            window = arr[i-window_size:i]
            mean = np.mean(window)
            std = np.std(window)
            
            # 如果当前点偏离平均值超过2倍标准差，标记为异常
            if std > 0 and abs(arr[i] - mean) > 2 * std:
                anomalies.append(i)
        
        return anomalies
    
    except Exception as e:
        logger.error(f"时间序列异常检测失败: {e}")
        return []

# master_panel/dashboard.py
import streamlit as st
import pandas as pd
import os
import json
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
from distribution.license_manager import LicenseManager

def authenticate():
    """验证主控身份"""
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        return True
        
    st.title("🔐 主控面板登录")
    
    master_key = st.text_input("请输入主控密钥", type="password")
    
    if st.button("登录"):
        if master_key == os.getenv("MASTER_KEY"):
            st.session_state["authenticated"] = True
            st.session_state["master_key"] = master_key
            st.rerun()
        else:
            st.error("密钥错误")
            
    return False

def load_telemetry_data():
    """加载遥测数据"""
    telemetry_dir = "data/telemetry"
    
    if not os.path.exists(telemetry_dir):
        return {"system_info": [], "feature_usage": [], "errors": []}
    
    system_info = []
    feature_usage = []
    errors = []
    
    for file in os.listdir(telemetry_dir):
        if not file.endswith(".json"):
            continue
            
        file_path = os.path.join(telemetry_dir, file)
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            if "system_info" in file:
                system_info.append(data)
            elif "feature_usage" in file:
                feature_usage.append(data)
            elif "error" in file:
                errors.append(data)
        except:
            pass
    
    return {
        "system_info": system_info,
        "feature_usage": feature_usage,
        "errors": errors
    }

def render_master_dashboard():
    """渲染主控面板"""
    st.set_page_config(page_title="跨境电商智能体 - 主控面板", layout="wide", page_icon="🔐")
    
    st.title("🔐 跨境电商智能体 - 主控面板")
    st.caption(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 登录用户: 2927093389zxq-boop")
    
    if not authenticate():
        return
    
    # 主控面板标签页
    tab1, tab2, tab3 = st.tabs([
        "📊 使用概览", 
        "👥 用户管理", 
        "⚠️ 错误报告"
    ])
    
    with tab1:
        st.header("📊 使用数据概览")
        
        # 获取遥测数据
        telemetry = load_telemetry_data()
        
        # 活跃用户统计
        active_instances = len(set([d.get("instance_id", "") for d in telemetry["system_info"]]))
        st.metric("活跃实例数", active_instances)
        
        # 使用频率统计
        feature_usage = telemetry["feature_usage"]
        if feature_usage:
            # 按功能分组统计使用次数
            feature_counts = {}
            for item in feature_usage:
                feature = item.get("feature", "未知")
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
                
            # 创建图表
            if feature_counts:
                fig, ax = plt.subplots()
                ax.bar(feature_counts.keys(), feature_counts.values())
                ax.set_title("功能使用频率")
                ax.set_xlabel("功能")
                ax.set_ylabel("使用次数")
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig)
        else:
            st.info("暂无功能使用数据")
    
    with tab2:
        st.header("👥 用户管理")
        
        # 加载许可证文件
        license_path = "license.json"
        if os.path.exists(license_path):
            with open(license_path, "r") as f:
                license_data = json.load(f)
                
            st.write("当前许可证信息:")
            st.write(f"用户名: {license_data['data'].get('name', 'N/A')}")
            st.write(f"邮箱: {license_data['data'].get('email', 'N/A')}")
            st.write(f"功能集: {license_data['data'].get('feature_set', 'N/A')}")
            st.write(f"过期日期: {license_data['data'].get('expires_at', 'N/A')}")
        else:
            st.info("未找到许可证文件")
        
        # 创建新许可证
        st.subheader("创建新许可证")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("用户名")
            email = st.text_input("邮箱")
        with col2:
            expiry_days = st.number_input("有效期(天)", min_value=1, value=365)
            feature_set = st.selectbox("功能集", ["standard", "professional", "enterprise"])
        
        if st.button("生成许可证"):
            if name and email:
                try:
                    license_manager = LicenseManager(master_key=st.session_state.get("master_key"))
                    license_data = license_manager.generate_license(
                        {"name": name, "email": email},
                        expiry_days=expiry_days,
                        feature_set=feature_set
                    )
                    
                    # 显示许可证信息
                    st.success("许可证生成成功!")
                    st.code(json.dumps(license_data, indent=2))
                    
                    # 提供下载功能
                    st.download_button(
                        "下载许可证文件",
                        json.dumps(license_data, indent=2),
                        file_name=f"license_{name.replace(' ', '_')}.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"生成许可证失败: {e}")
            else:
                st.warning("请填写用户名和邮箱")
    
    with tab3:
        st.header("⚠️ 错误报告")
        
        # 获取错误数据
        errors = telemetry["errors"]
        
        if errors:
            # 显示错误表格
            error_data = []
            for error in errors:
                error_data.append({
                    "实例ID": error.get("instance_id", "未知"),
                    "错误类型": error.get("error_type", "未知"),
                    "错误消息": error.get("message", "未知"),
                    "时间": error.get("timestamp", "未知").replace("T", " ").split(".")[0] if isinstance(error.get("timestamp"), str) else "未知"
                })
                
            st.dataframe(pd.DataFrame(error_data))
            
            # 查看详细错误信息
            if error_data:
                selected_index = st.selectbox(
                    "选择要查看详细信息的错误", 
                    range(len(error_data)),
                    format_func=lambda i: f"{error_data[i]['错误类型']} - {error_data[i]['时间']}"
                )
                
                st.json(errors[selected_index])
        else:
            st.info("暂无错误报告数据")

# 如果直接运行此脚本
if __name__ == "__main__":
    render_master_dashboard()
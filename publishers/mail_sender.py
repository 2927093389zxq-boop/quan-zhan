# publishers/mail_sender.py
import smtplib, json, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, cfg_path="config/config.json"):
    if not os.path.exists(cfg_path):
        raise Exception("找不到 config/config.json")
    cfg = json.load(open(cfg_path,"r",encoding="utf-8"))
    email_cfg = cfg.get("email",{})
    sender = email_cfg.get("sender")
    password = email_cfg.get("password")
    receiver = email_cfg.get("receiver")
    smtp = email_cfg.get("smtp_server")
    port = email_cfg.get("smtp_port",465)

    if not (sender and password and receiver and smtp):
        raise Exception("邮件配置不完整，请在 config/config.json 中填写")

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))

    # 若存在演化摘要，附加
    evo_path = "logs/evolution_suggestions.json"
    if os.path.exists(evo_path):
        try:
            evo = json.load(open(evo_path,"r",encoding="utf-8"))
            suggestions = evo.get("suggestions","")
            body_extra = f"<hr><h4>AI 自主进化摘要</h4><pre>{suggestions}</pre>"
            msg.attach(MIMEText(body_extra, "html", "utf-8"))
        except:
            pass

    server = smtplib.SMTP_SSL(smtp, port, timeout=30)
    server.login(sender, password)
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()
    print("[Mail] 邮件已发送到", receiver)

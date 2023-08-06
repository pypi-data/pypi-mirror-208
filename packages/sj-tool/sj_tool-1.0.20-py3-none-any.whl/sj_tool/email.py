from typing import List
import yagmail


def send_email(user: str, password: str, receiver: List[str], contents: List[str], host="smtp.163.com", subject="系统报警"):
    # 邮件配置信息
    yag = yagmail.SMTP(user=user, password=password, host=host)
    # 构造邮件内容
    attachments = []
    # 发送邮件
    r = yag.send(to=receiver, subject=subject, contents=contents, attachments=attachments)
    if r:
        return True
    return False

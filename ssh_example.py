"""
SSH连接示例
演示如何通过SSH连接智能车并发送PID参数
"""

from app.services.ssh_service import SSHService
from app.services.protocol_parser import ProtocolParser

def ssh_connection_example():
    """SSH连接示例"""
    # 创建SSH服务
    ssh = SSHService()
    
    # 连接到远程服务器
    # 注意：需要替换为实际的服务器信息
    host = "192.168.1.100"  # 智能车IP地址
    port = 22
    username = "root"
    password = "your_password"  # 或使用key_file
    
    print(f"正在连接SSH服务器 {host}...")
    
    # 连接（取消注释以下行以实际连接）
    # success = ssh.connect(host, port, username, password)
    # if not success:
    #     print("SSH连接失败")
    #     return
    
    print("SSH连接示例（未实际连接）")
    
    # 示例：通过SSH发送PID参数
    # 假设智能车使用串口设备 /dev/ttyUSB0
    parser = ProtocolParser()
    
    # PID参数
    p = 1.5
    i = 0.2
    d = 0.05
    
    # 创建PID命令
    command = f"echo 'P={p:.2f},I={i:.2f},D={d:.2f}' > /dev/ttyUSB0"
    print(f"发送命令: {command}")
    
    # 执行命令（取消注释以实际执行）
    # result = ssh.execute_command(command)
    # if result['success']:
    #     print("命令执行成功")
    # else:
    #     print(f"命令执行失败: {result['error']}")
    
    # 示例：发送原始数据
    data = b"P=1.50,I=0.20,D=0.05"
    print(f"发送数据: {data}")
    
    # 发送数据（取消注释以实际发送）
    # ssh.send_data(data)
    
    # 断开连接（取消注释以实际断开）
    # ssh.disconnect()
    
    print("SSH连接示例完成")

if __name__ == "__main__":
    ssh_connection_example()
# 智能车上位机调试软件

使用mimocode+mimo-v2.5模型制作的测试软件
基于Python+PyQt的跨平台上位机调试软件，用于智能车PID参数调试。

## 功能特性

- **连接方式**：
  - 串口通信：支持多种串口配置
  - SSH连接：支持远程服务器连接调参
- **状态反馈**：
  - 彩色状态提示：连接成功绿色、失败红色、默认灰色
  - 按钮互斥：连接/断开自动切换
- 实时PID曲线：P、I、D三条曲线实时显示
- 参数调节：滑块和输入框实时调节PID参数
- 数据记录：支持TXT、CSV、JSON多种格式
- 自动调参：基于Ziegler-Nichols等算法
- 跨平台：支持Windows、macOS、Linux

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

## 开发

### 运行测试

```bash
python run_tests.py
```

### 项目结构

```
smart_car_debugger/
├── main.py                # 应用入口
├── app/                   # 应用代码
├── tests/                 # 测试代码
├── docs/                  # 文档
└── requirements.txt       # 依赖
```

## 许可证

MIT License

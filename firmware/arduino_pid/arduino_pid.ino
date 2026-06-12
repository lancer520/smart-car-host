/*
 * 智能车PID调参示例 - Arduino版本
 * 
 * 功能：
 * 1. 通过串口接收上位机发送的PID参数
 * 2. 实时发送PID数据给上位机
 * 3. 实现基本的速度PID控制
 * 
 * 硬件连接：
 * - 电机驱动：PWM引脚9, 10
 * - 编码器：中断引脚2, 3
 * - 串口：115200波特率
 */

// ============ 引脚定义 ============
#define ENA 9    // 左电机PWM
#define IN1 8    // 左电机方向
#define IN2 7
#define ENB 10   // 右电机PWM
#define IN3 6    // 右电机方向
#define IN4 5

#define ENCODER_LEFT_A 2   // 左编码器A相（中断）
#define ENCODER_LEFT_B 4   // 左编码器B相
#define ENCODER_RIGHT_A 3  // 右编码器A相（中断）
#define ENCODER_RIGHT_B 11 // 右编码器B相

// ============ PID参数 ============
float Kp = 1.0;    // 比例系数
float Ki = 0.1;    // 积分系数
float Kd = 0.01;   // 微分系数

// ============ 控制变量 ============
volatile long encoder_left_count = 0;
volatile long encoder_right_count = 0;

float target_speed = 100.0;   // 目标速度
float current_speed = 0.0;    // 当前速度
float error = 0.0;            // 误差
float last_error = 0.0;       // 上次误差
float integral = 0.0;         // 积分项
float derivative = 0.0;       // 微分项
float output = 0.0;           // PID输出

unsigned long last_time = 0;
unsigned long sample_time = 50;  // 采样周期50ms

// ============ 串口接收缓冲 ============
String input_string = "";
boolean string_complete = false;

// ============ 初始化 ============
void setup() {
  // 串口初始化
  Serial.begin(115200);
  input_string.reserve(200);
  
  // 电机引脚
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // 编码器引脚
  pinMode(ENCODER_LEFT_A, INPUT_PULLUP);
  pinMode(ENCODER_LEFT_B, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_A, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_B, INPUT_PULLUP);
  
  // 中断设置
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A), encoder_left_isr, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), encoder_right_isr, RISING);
  
  // 设置前进方向
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  
  last_time = millis();
  
  Serial.println("Smart Car PID Controller Started");
  Serial.println("Format: P=1.00,I=0.10,D=0.01");
}

// ============ 编码器中断服务 ============
void encoder_left_isr() {
  if (digitalRead(ENCODER_LEFT_B)) {
    encoder_left_count++;
  } else {
    encoder_left_count--;
  }
}

void encoder_right_isr() {
  if (digitalRead(ENCODER_RIGHT_B)) {
    encoder_right_count++;
  } else {
    encoder_right_count--;
  }
}

// ============ 主循环 ============
void loop() {
  // 处理串口接收
  serial_receive();
  
  // 定时计算PID
  unsigned long current_time = millis();
  if (current_time - last_time >= sample_time) {
    // 计算当前速度（脉冲数/50ms）
    current_speed = (encoder_left_count + encoder_right_count) / 2.0;
    
    // 重置编码器
    encoder_left_count = 0;
    encoder_right_count = 0;
    
    // 计算PID
    pid_calculate();
    
    // 控制电机
    motor_control(output);
    
    // 发送数据给上位机
    send_data();
    
    last_time = current_time;
  }
}

// ============ PID计算 ============
void pid_calculate() {
  // 计算误差
  error = target_speed - current_speed;
  
  // 积分项（带抗饱和）
  integral += error * sample_time / 1000.0;
  integral = constrain(integral, -1000, 1000);  // 限制积分项
  
  // 微分项
  derivative = (error - last_error) / (sample_time / 1000.0);
  
  // PID输出
  output = Kp * error + Ki * integral + Kd * derivative;
  
  // 限制输出范围
  output = constrain(output, -255, 255);
  
  // 保存上次误差
  last_error = error;
}

// ============ 电机控制 ============
void motor_control(float speed) {
  if (speed > 0) {
    // 前进
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, (int)speed);
    analogWrite(ENB, (int)speed);
  } else if (speed < 0) {
    // 后退
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, (int)(-speed));
    analogWrite(ENB, (int)(-speed));
  } else {
    // 停止
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
  }
}

// ============ 串口接收处理 ============
void serial_receive() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      string_complete = true;
    } else {
      input_string += inChar;
    }
  }
  
  if (string_complete) {
    parse_command(input_string);
    input_string = "";
    string_complete = false;
  }
}

// ============ 解析指令 ============
void parse_command(String cmd) {
  cmd.trim();
  
  // 检查是否是PID参数设置
  if (cmd.indexOf('P=') >= 0 && cmd.indexOf('I=') >= 0) {
    // 解析 P=1.00,I=0.10,D=0.01
    int p_start = cmd.indexOf('P=') + 2;
    int p_end = cmd.indexOf(',');
    int i_start = cmd.indexOf('I=') + 2;
    int i_end = cmd.indexOf(',', i_start);
    int d_start = cmd.indexOf('D=') + 2;
    
    if (p_start > 1 && i_start > 1 && d_start > 1) {
      float new_p = cmd.substring(p_start, p_end).toFloat();
      float new_i = cmd.substring(i_start, i_end).toFloat();
      float new_d = cmd.substring(d_start).toFloat();
      
      // 设置新参数
      Kp = new_p;
      Ki = new_i;
      Kd = new_d;
      
      // 重置积分项
      integral = 0;
      
      // 回显确认
      Serial.print("PID Updated: P=");
      Serial.print(Kp, 2);
      Serial.print(", I=");
      Serial.print(Ki, 2);
      Serial.print(", D=");
      Serial.println(Kd, 2);
    }
  }
  // 其他命令
  else if (cmd == "STATUS") {
    // 发送状态
    send_status();
  }
  else if (cmd == "RESET") {
    // 重置PID
    integral = 0;
    last_error = 0;
    Serial.println("PID Reset");
  }
  else if (cmd == "STOP") {
    // 停止电机
    motor_control(0);
    Serial.println("Motor Stopped");
  }
  else if (cmd.startsWith("SETPOINT=")) {
    // 设置目标速度
    float new_setpoint = cmd.substring(9).toFloat();
    target_speed = new_setpoint;
    Serial.print("Target Speed: ");
    Serial.println(target_speed);
  }
}

// ============ 发送数据给上位机 ============
void send_data() {
  // 格式: P=1.00,I=0.10,D=0.01,actual=95.50,target=100.00,error=4.50
  Serial.print("P=");
  Serial.print(Kp, 2);
  Serial.print(",I=");
  Serial.print(Ki, 2);
  Serial.print(",D=");
  Serial.print(Kd, 2);
  Serial.print(",actual=");
  Serial.print(current_speed, 2);
  Serial.print(",target=");
  Serial.print(target_speed, 2);
  Serial.print(",error=");
  Serial.println(error, 2);
}

// ============ 发送状态 ============
void send_status() {
  Serial.println("=== Status ===");
  Serial.print("PID: P=");
  Serial.print(Kp, 2);
  Serial.print(", I=");
  Serial.print(Ki, 2);
  Serial.print(", D=");
  Serial.println(Kd, 2);
  Serial.print("Target: ");
  Serial.println(target_speed);
  Serial.print("Current: ");
  Serial.println(current_speed);
  Serial.print("Error: ");
  Serial.println(error);
  Serial.print("Output: ");
  Serial.println(output);
  Serial.println("==============");
}
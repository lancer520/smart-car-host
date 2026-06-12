/**
 * 智能车PID调参示例 - STM32版本
 * 
 * 功能：
 * 1. 通过串口接收上位机发送的PID参数
 * 2. 实时发送PID数据给上位机
 * 3. 实现基本的速度PID控制
 * 
 * 硬件：STM32F103C8T6
 * 串口：USART1 (PA9/PA10) 115200波特率
 * 电机：TIM2 PWM (PA0/PA1)
 * 编码器：TIM3/TIM4 编码器模式
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// ============ PID参数 ============
float Kp = 1.0f;
float Ki = 0.1f;
float Kd = 0.01f;

// ============ 控制变量 ============
volatile int32_t encoder_left_count = 0;
volatile int32_t encoder_right_count = 0;

float target_speed = 100.0f;
float current_speed = 0.0f;
float error = 0.0f;
float last_error = 0.0f;
float integral = 0.0f;
float derivative = 0.0f;
float pid_output = 0.0f;

uint32_t last_tick = 0;
uint32_t sample_time = 50;  // 50ms

// ============ 串口接收 ============
UART_HandleTypeDef huart1;
char rx_buffer[128];
volatile uint8_t rx_index = 0;
volatile uint8_t rx_complete = 0;

// ============ 定时器 ============
TIM_HandleTypeDef htim2;  // 电机PWM
TIM_HandleTypeDef htim3;  // 左编码器
TIM_HandleTypeDef htim4;  // 右编码器

// ============ 函数声明 ============
void SystemClock_Config(void);
void GPIO_Init(void);
void USART1_Init(void);
void TIM2_Init(void);
void TIM3_Init(void);
void TIM4_Init(void);
void PID_Calculate(void);
void Motor_Control(float speed);
void Parse_Command(char* cmd);
void Send_Data(void);
void Send_Status(void);

// ============ 主函数 ============
int main(void) {
  HAL_Init();
  SystemClock_Config();
  GPIO_Init();
  USART1_Init();
  TIM2_Init();
  TIM3_Init();
  TIM4_Init();
  
  // 启动编码器
  HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
  HAL_TIM_Encoder_Start(&htim4, TIM_CHANNEL_ALL);
  
  // 启动PWM
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
  
  // 启动串口接收中断
  HAL_UART_Receive_IT(&huart1, (uint8_t*)&rx_buffer[rx_index], 1);
  
  last_tick = HAL_GetTick();
  
  // 发送启动信息
  char* msg = "STM32 PID Controller Started\r\nFormat: P=1.00,I=0.10,D=0.01\r\n";
  HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), 100);
  
  while (1) {
    // 处理串口接收
    if (rx_complete) {
      Parse_Command(rx_buffer);
      rx_index = 0;
      rx_complete = 0;
      memset(rx_buffer, 0, sizeof(rx_buffer));
      HAL_UART_Receive_IT(&huart1, (uint8_t*)&rx_buffer[0], 1);
    }
    
    // 定时计算PID
    uint32_t current_tick = HAL_GetTick();
    if (current_tick - last_tick >= sample_time) {
      // 读取编码器
      int32_t left = (int32_t)htim3.Instance->CNT;
      int32_t right = (int32_t)htim4.Instance->CNT;
      
      // 计算速度
      current_speed = (float)(left + right) / 2.0f;
      
      // 重置编码器
      __HAL_TIM_SET_COUNTER(&htim3, 0);
      __HAL_TIM_SET_COUNTER(&htim4, 0);
      
      // 计算PID
      PID_Calculate();
      
      // 控制电机
      Motor_Control(pid_output);
      
      // 发送数据
      Send_Data();
      
      last_tick = current_tick;
    }
  }
}

// ============ PID计算 ============
void PID_Calculate(void) {
  error = target_speed - current_speed;
  
  // 积分项（带抗饱和）
  integral += error * sample_time / 1000.0f;
  if (integral > 1000.0f) integral = 1000.0f;
  if (integral < -1000.0f) integral = -1000.0f;
  
  // 微分项
  derivative = (error - last_error) / (sample_time / 1000.0f);
  
  // PID输出
  pid_output = Kp * error + Ki * integral + Kd * derivative;
  
  // 限制输出
  if (pid_output > 255.0f) pid_output = 255.0f;
  if (pid_output < -255.0f) pid_output = -255.0f;
  
  last_error = error;
}

// ============ 电机控制 ============
void Motor_Control(float speed) {
  uint32_t pwm_value;
  
  if (speed > 0) {
    // 前进
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_6, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, GPIO_PIN_RESET);
    pwm_value = (uint32_t)speed;
  } else if (speed < 0) {
    // 后退
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_6, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, GPIO_PIN_SET);
    pwm_value = (uint32_t)(-speed);
  } else {
    pwm_value = 0;
  }
  
  if (pwm_value > 255) pwm_value = 255;
  
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pwm_value);
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pwm_value);
}

// ============ 解析指令 ============
void Parse_Command(char* cmd) {
  // 去除换行符
  char* p = strchr(cmd, '\r');
  if (p) *p = 0;
  p = strchr(cmd, '\n');
  if (p) *p = 0;
  
  // 检查PID参数
  if (strstr(cmd, "P=") && strstr(cmd, "I=")) {
    char* p_str = strstr(cmd, "P=") + 2;
    char* i_str = strstr(cmd, "I=") + 2;
    char* d_str = strstr(cmd, "D=") + 2;
    
    Kp = atof(p_str);
    Ki = atof(i_str);
    Kd = atof(d_str);
    
    integral = 0;  // 重置积分项
    
    char buf[64];
    sprintf(buf, "PID Updated: P=%.2f, I=%.2f, D=%.2f\r\n", Kp, Ki, Kd);
    HAL_UART_Transmit(&huart1, (uint8_t*)buf, strlen(buf), 100);
  }
  else if (strcmp(cmd, "STATUS") == 0) {
    Send_Status();
  }
  else if (strcmp(cmd, "RESET") == 0) {
    integral = 0;
    last_error = 0;
    char* msg = "PID Reset\r\n";
    HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), 100);
  }
  else if (strcmp(cmd, "STOP") == 0) {
    Motor_Control(0);
    char* msg = "Motor Stopped\r\n";
    HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), 100);
  }
  else if (strstr(cmd, "SETPOINT=")) {
    char* val_str = strstr(cmd, "SETPOINT=") + 9;
    target_speed = atof(val_str);
    char buf[32];
    sprintf(buf, "Target: %.1f\r\n", target_speed);
    HAL_UART_Transmit(&huart1, (uint8_t*)buf, strlen(buf), 100);
  }
}

// ============ 发送数据 ============
void Send_Data(void) {
  char buf[128];
  sprintf(buf, "P=%.2f,I=%.2f,D=%.2f,actual=%.2f,target=%.2f,error=%.2f\r\n",
          Kp, Ki, Kd, current_speed, target_speed, error);
  HAL_UART_Transmit(&huart1, (uint8_t*)buf, strlen(buf), 100);
}

// ============ 发送状态 ============
void Send_Status(void) {
  char buf[256];
  sprintf(buf, 
    "=== Status ===\r\n"
    "PID: P=%.2f, I=%.2f, D=%.2f\r\n"
    "Target: %.1f\r\n"
    "Current: %.1f\r\n"
    "Error: %.1f\r\n"
    "Output: %.1f\r\n"
    "==============\r\n",
    Kp, Ki, Kd, target_speed, current_speed, error, pid_output);
  HAL_UART_Transmit(&huart1, (uint8_t*)buf, strlen(buf), 100);
}

// ============ 串口接收回调 ============
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USART1) {
    if (rx_buffer[rx_index] == '\n') {
      rx_complete = 1;
    } else {
      rx_index++;
      if (rx_index >= sizeof(rx_buffer) - 1) {
        rx_index = 0;
      }
      HAL_UART_Receive_IT(&huart1, (uint8_t*)&rx_buffer[rx_index], 1);
    }
  }
}

// ============ 系统时钟配置 ============
void SystemClock_Config(void) {
  // 配置为72MHz
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);
  
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

// ============ GPIO初始化 ============
void GPIO_Init(void) {
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  
  // 电机方向引脚
  GPIO_InitStruct.Pin = GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

// ============ 串口初始化 ============
void USART1_Init(void) {
  __HAL_RCC_USART1_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_9;   // TX
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  GPIO_InitStruct.Pin = GPIO_PIN_10;  // RX
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  HAL_UART_Init(&huart1);
}

// ============ TIM2初始化（电机PWM） ============
void TIM2_Init(void) {
  __HAL_RCC_TIM2_CLK_ENABLE();
  
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1;  // CH1, CH2
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 71;        // 72MHz/72 = 1MHz
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 255;          // 1MHz/256 = 3.9kHz
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_PWM_Init(&htim2);
  
  TIM_OC_InitTypeDef sConfigOC = {0};
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1);
  HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_2);
}

// ============ TIM3初始化（左编码器） ============
void TIM3_Init(void) {
  __HAL_RCC_TIM3_CLK_ENABLE();
  
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_6|GPIO_PIN_7;  // A, B
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 0xFFFF;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_Encoder_Init(&htim3);
}

// ============ TIM4初始化（右编码器） ============
void TIM4_Init(void) {
  __HAL_RCC_TIM4_CLK_ENABLE();
  
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_6|GPIO_PIN_7;  // A, B
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
  
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 0;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 0xFFFF;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_Encoder_Init(&htim4);
}
#include "esp_camera.h"
#include "esp_log.h"

// 摄像头引脚配置（根据你开发板修改，通用配置如下）
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      15
#define SIOD_GPIO_NUM     4
#define SIOC_GPIO_NUM     5
#define Y9_GPIO_NUM       16
#define Y8_GPIO_NUM       17
#define Y7_GPIO_NUM       18
#define Y6_GPIO_NUM       12
#define Y5_GPIO_NUM       10
#define Y4_GPIO_NUM       8
#define Y3_GPIO_NUM       9
#define Y2_GPIO_NUM       11
#define VSYNC_GPIO_NUM    6
#define HREF_GPIO_NUM     7
#define PCLK_GPIO_NUM     13

static const char *TAG = "CAMERA_DEMO";

void app_main(void) {
    // 1. 摄像头配置
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;  // XCLK时钟
    config.pixel_format = PIXFORMAT_JPEG;  // 输出JPEG格式

    // 2. 分辨率选择（根据摄像头型号调整）
    config.frame_size = FRAMESIZE_QVGA;  // 320x240（通用）
    config.jpeg_quality = 10;  // 画质0-63，数值越小画质越好
    config.fb_count = 2;  // 双缓冲

    // 3. 初始化摄像头
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "摄像头初始化失败！错误码: %s", esp_err_to_name(err));
        return;
    }

    ESP_LOGI(TAG, "摄像头初始化成功！");
    sensor_t *s = esp_camera_sensor_get();
    // 可选：调整摄像头参数（亮度、对比度等）
    s->set_brightness(s, 0);
    s->set_saturation(s, 0);

    while (1) {
        // 4. 获取一帧图像
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb) {
            ESP_LOGI(TAG, "获取帧成功！分辨率: %dx%d，大小: %zu字节", fb->width, fb->height, fb->len);
            esp_camera_fb_return(fb);  // 释放帧缓冲区
        } else {
            ESP_LOGE(TAG, "获取帧失败！");
        }
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

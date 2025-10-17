# 爬虫增强配置说明

## 运行前必填（任选）
1. MongoDB:
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=amazon_crawl
   MONGO_COLLECTION=products

2. MySQL:
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=yourpass
   MYSQL_DB=amazon_crawl

3. 云存储 (示例 S3 / MinIO):
   S3_ENDPOINT=http://127.0.0.1:9000
   S3_ACCESS_KEY=minioadmin
   S3_SECRET_KEY=minioadmin
   S3_BUCKET=amazon-data

4. 2Captcha 验证码：
   CAPTCHA_API_KEY=YOUR_2CAPTCHA_KEY

5. 采集策略：
   MAX_CONCURRENT_DETAIL=4
   DETAIL_RETRY=2
   REQUEST_DELAY_MIN=1.0
   REQUEST_DELAY_MAX=2.2

## 存储模式
local / mongo / mysql / cloud

在 UI 中选择对应模式后会自动调用。
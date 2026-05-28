# Evaluation Report: task_company_weekly_sales_performance

- Total score: 4.00 / 18.00
- Accuracy: 22.22%

## Turn 0

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明当前周期为 2023-10-15 至 2023-10-21。

Reason: 模型给出的当前周起止日期为2023-10-16至2023-10-22，与score_point明确要求的2023-10-15至2023-10-21不一致。

Missing:
- 当前周期为 2023-10-15 至 2023-10-21

## Turn 1

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明上一周期为 2023-10-08 至 2023-10-14。

Reason: 模型回答的上一周起止日期为2023-10-09至2023-10-15，与score_point要求的2023-10-08至2023-10-14不一致。

Matched:
- 上一周（对照周）起止日期：2023-10-09（周一）至 2023-10-15（周日）

Missing:
- 上一周期为 2023-10-08 至 2023-10-14

## Turn 2

- Score: 0.00 / 11.00
- Accuracy: 0.00%

### 1. FAIL

本周总销售额需要为 169593.16。

Reason: 本周总销售额数值不匹配

Matched:
- 本周总销售额 $137,823

Missing:
- 数值应为 169593.16

### 2. FAIL

上一周总销售额需要为 100522.33。

Reason: 上一周总销售额数值不匹配

Matched:
- 上周总销售额 $131,657

Missing:
- 数值应为 100522.33

### 3. FAIL

销售额环比变化率需要为 68.71。

Reason: 销售额环比变化率数值不匹配

Matched:
- 环比变化 +4.7%

Missing:
- 数值应为 68.71

### 4. FAIL

本周订单行数需要为 30。

Reason: 本周订单行数数值不匹配

Matched:
- 订单行 27

Missing:
- 数值应为 30

### 5. FAIL

本周销量需要为 879。

Reason: 本周销量数值不匹配

Matched:
- 总销量 756

Missing:
- 数值应为 879

### 6. FAIL

本周平均折扣率需要为 14.07。

Reason: 本周平均折扣率数值不匹配

Matched:
- 平均折扣 15.67%

Missing:
- 数值应为 14.07

### 7. FAIL

销售额最高销售代表需要对应 David，数值为 80190.91。

Reason: 销售额最高销售代表数值不匹配

Matched:
- David $56,849

Missing:
- 数值应为 80190.91

### 8. FAIL

销售额最高区域需要对应 North，数值为 62213.15。

Reason: 销售额最高区域数值不匹配

Matched:
- North $51,850

Missing:
- 数值应为 62213.15

### 9. FAIL

销售额最高品类需要对应 Clothing，数值为 57726.17。

Reason: 销售额最高品类数值不匹配

Matched:
- Clothing $54,518

Missing:
- 数值应为 57726.17

### 10. FAIL

Retail 渠道销售额需要对应 Retail，数值为 112731.84。

Reason: Retail渠道销售额数值不匹配

Matched:
- Retail $107,123

Missing:
- 数值应为 112731.84

### 11. FAIL

Returning 客户销售额需要对应 Returning，数值为 106867.76。

Reason: Returning客户销售额数值不匹配

Matched:
- Returning $95,316

Missing:
- 数值应为 106867.76

## Turn 3

- Score: 4.00 / 5.00
- Accuracy: 80.00%

### 1. PASS

重点词或实体清单需要包含 David。

Reason: 回答中包含了实体 David

Matched:
- Charlie/David 下滑
- David -23.1%

### 2. FAIL

重点词或实体清单需要包含 North。

Reason: 回答中未包含实体 North

Missing:
- North

### 3. PASS

重点词或实体清单需要包含 Clothing。

Reason: 回答中包含了实体 Clothing

Matched:
- Clothing/Food 接力
- Clothing +46.2%

### 4. PASS

重点词或实体清单需要包含 Retail。

Reason: 回答中包含了实体 Retail

Matched:
- Retail 取代 Online 成主渠道
- Retail +140.4%

### 5. PASS

重点词或实体清单需要包含 Returning。

Reason: 回答中包含了实体 Returning

Matched:
- Returning 客户贡献大幅提升
- Returning +25.3%

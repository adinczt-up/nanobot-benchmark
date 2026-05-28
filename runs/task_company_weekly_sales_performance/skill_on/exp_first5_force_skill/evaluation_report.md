# Evaluation Report: task_company_weekly_sales_performance

- Total score: 3.00 / 18.00
- Accuracy: 16.67%

## Turn 0

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明当前周期为 2023-10-15 至 2023-10-21。

Reason: 模型给出的当前周起止日期错误，与评分点要求的日期不一致。

Missing:
- 当前周期为 2023-10-15 至 2023-10-21

## Turn 1

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明上一周期为 2023-10-08 至 2023-10-14。

Reason: 模型回答的上一周时间窗为2023-10-16至2023-10-22，与要求的2023-10-08至2023-10-14不符

Matched:
- 上一周（对照） | 2023-10-16 ~ 2023-10-22

Missing:
- 上一周期为 2023-10-08 至 2023-10-14

## Turn 2

- Score: 0.00 / 11.00
- Accuracy: 0.00%

### 1. FAIL

本周总销售额需要为 169593.16。

Reason: 本周总销售额数值不匹配

Matched:
- 总销售额 | $94,875.48

Missing:
- 169593.16

### 2. FAIL

上一周总销售额需要为 100522.33。

Reason: 上一周总销售额数值不匹配

Matched:
- 上周 (10/16–10/22) | $137,823.36

Missing:
- 100522.33

### 3. FAIL

销售额环比变化率需要为 68.71。

Reason: 销售额环比变化率数值不匹配

Matched:
- -31.2%

Missing:
- 68.71

### 4. FAIL

本周订单行数需要为 30。

Reason: 本周订单行数数值不匹配

Matched:
- 订单行 | 19

Missing:
- 30

### 5. FAIL

本周销量需要为 879。

Reason: 本周销量数值不匹配

Matched:
- 销量（件） | 587

Missing:
- 879

### 6. FAIL

本周平均折扣率需要为 14.07。

Reason: 本周平均折扣率数值不匹配

Matched:
- 平均折扣 | 16.68%

Missing:
- 14.07

### 7. FAIL

销售额最高销售代表需要对应 David，数值为 80190.91。

Reason: 销售额最高销售代表数值不匹配

Matched:
- David | $47,974.20

Missing:
- 80190.91

### 8. FAIL

销售额最高区域需要对应 North，数值为 62213.15。

Reason: 销售额最高区域数值不匹配

Matched:
- North | $26,870.65

Missing:
- 62213.15

### 9. FAIL

销售额最高品类需要对应 Clothing，数值为 57726.17。

Reason: 销售额最高品类及数值均不匹配

Matched:
- 1 | Food | $37,775.58
- 2 | Clothing | $26,010.32

Missing:
- 最高品类为Clothing
- 57726.17

### 10. FAIL

Retail 渠道销售额需要对应 Retail，数值为 112731.84。

Reason: Retail渠道销售额数值不匹配

Matched:
- Retail | $64,745.74

Missing:
- 112731.84

### 11. FAIL

Returning 客户销售额需要对应 Returning，数值为 106867.76。

Reason: Returning客户销售额数值不匹配

Matched:
- Returning | $54,556.51

Missing:
- 106867.76

## Turn 3

- Score: 3.00 / 5.00
- Accuracy: 60.00%

### 1. FAIL

重点词或实体清单需要包含 David。

Reason: 模型回答的关键词或实体清单中未包含 David

Missing:
- David

### 2. FAIL

重点词或实体清单需要包含 North。

Reason: 模型回答的关键词或实体清单中未包含 North

Missing:
- North

### 3. PASS

重点词或实体清单需要包含 Clothing。

Reason: 模型回答的风险/下滑标签中包含了 Clothing

Matched:
- Clothing / Electronics 腰斩

### 4. PASS

重点词或实体清单需要包含 Retail。

Reason: 模型回答的风险/下滑标签中包含了 Retail

Matched:
- Retail 渠道失速

### 5. PASS

重点词或实体清单需要包含 Returning。

Reason: 模型回答的风险/下滑标签中包含了 Returning

Matched:
- Returning 客户 -42.8%

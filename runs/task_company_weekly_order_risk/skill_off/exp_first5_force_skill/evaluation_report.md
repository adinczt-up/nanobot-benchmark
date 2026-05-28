# Evaluation Report: task_company_weekly_order_risk

- Total score: 5.00 / 20.00
- Accuracy: 25.00%

## Turn 0

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明当前周期为 2005-05-08 至 2005-05-14。

Reason: 模型回答的当前周日期范围为2005-05-17至2005-05-31，与score_point要求的2005-05-08至2005-05-14不符。

Missing:
- 当前周期为2005-05-08至2005-05-14

## Turn 1

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明上一周期为 2005-05-01 至 2005-05-07。

Reason: 模型回答的上一周日期范围为5月1日至5月13日，未满足score point明确要求的5月1日至5月7日。

Missing:
- 上一周期为 2005-05-01 至 2005-05-07

## Turn 2

- Score: 0.00 / 12.00
- Accuracy: 0.00%

### 1. FAIL

本周总销售额需要为 87709.93。

Reason: 本周总销售额数值错误

Missing:
- 本周总销售额需要为 87709.93，模型回答为 204,205

### 2. FAIL

上一周总销售额需要为 165946.07。

Reason: 上一周总销售额数值错误

Missing:
- 上一周总销售额需要为 165946.07，模型回答为 253,656

### 3. FAIL

销售额环比变化率需要为 -47.15。

Reason: 销售额环比变化率数值错误

Missing:
- 销售额环比变化率需要为 -47.15，模型回答为 -19.5%

### 4. FAIL

本周订单行数需要为 25。

Reason: 本周订单行数数值错误

Missing:
- 本周订单行数需要为 25，模型回答为 55

### 5. FAIL

本周唯一订单数需要为 3。

Reason: 本周唯一订单数数值错误

Missing:
- 本周唯一订单数需要为 3，模型回答为 7

### 6. FAIL

Disputed 状态订单行数需要对应 Disputed，数值为 11。

Reason: Disputed状态订单行数缺失或错误

Missing:
- Disputed状态订单行数需要为 11，模型未提供该数据

### 7. FAIL

Disputed 状态销售额需要对应 Disputed，数值为 46199.99。

Reason: Disputed状态销售额数值错误

Missing:
- Disputed状态销售额需要为 46199.99，模型回答为 46,200

### 8. FAIL

Shipped 状态销售额需要对应 Shipped，数值为 41509.94。

Reason: Shipped状态销售额数值错误

Missing:
- Shipped状态销售额需要为 41509.94，模型回答为 59,475 或 159,139

### 9. FAIL

销售额最高产品线需要对应 Motorcycles，数值为 39389.7。

Reason: 销售额最高产品线及数值错误

Missing:
- 销售额最高产品线需为 Motorcycles (39389.7)，模型回答为 Classic Cars

### 10. FAIL

销售额最高国家需要对应 Italy，数值为 41509.94。

Reason: 销售额最高国家及数值错误

Missing:
- 销售额最高国家需为 Italy (41509.94)，模型回答为 Austria

### 11. FAIL

主要风险客户需要对应 Euro Shopping Channel，数值为 31821.9。

Reason: 主要风险客户数值错误

Missing:
- 主要风险客户 Euro Shopping Channel 数值需为 31821.9，模型回答为 31,822

### 12. FAIL

亚太风险客户需要对应 Australian Collectables，数值为 14378.09。

Reason: 亚太风险客户数值错误

Missing:
- 亚太风险客户 Australian Collectables 数值需为 14378.09，模型回答为 14,378

## Turn 3

- Score: 5.00 / 6.00
- Accuracy: 83.33%

### 1. PASS

重点词或实体清单需要包含 Disputed。

Reason: 回答中包含了 Disputed

Matched:
- Disputed 遗留 46,200

### 2. PASS

重点词或实体清单需要包含 Euro Shopping Channel。

Reason: 回答中包含了 Euro Shopping Channel

Matched:
- Euro Shopping Channel

### 3. PASS

重点词或实体清单需要包含 Australian Collectables。

Reason: 回答中包含了 Australian Collectables

Matched:
- Australian Collectables, Ltd

### 4. PASS

重点词或实体清单需要包含 Motorcycles。

Reason: 回答中包含了 Motorcycles

Matched:
- Motorcycles / Planes / Ships / Trains

### 5. FAIL

重点词或实体清单需要包含 Italy。

Reason: 回答中未包含 Italy

Missing:
- Italy

### 6. PASS

重点词或实体清单需要包含 Spain。

Reason: 回答中包含了 Spain

Matched:
- Spain

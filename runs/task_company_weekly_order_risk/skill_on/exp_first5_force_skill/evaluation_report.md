# Evaluation Report: task_company_weekly_order_risk

- Total score: 6.00 / 20.00
- Accuracy: 30.00%

## Turn 0

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明当前周期为 2005-05-08 至 2005-05-14。

Reason: 模型回答的当前周日期范围为5月17日至31日，与score_point要求的2005-05-08至2005-05-14不符。

Missing:
- 当前周期为 2005-05-08 至 2005-05-14

## Turn 1

- Score: 0.00 / 1.00
- Accuracy: 0.00%

### 1. FAIL

答案需要说明上一周期为 2005-05-01 至 2005-05-07。

Reason: 模型回答的上一周结束日期为5月13日，与score_point要求的5月7日不一致

Matched:
- 上一周日期范围：2005年5月1日 – 5月13日

Missing:
- 上一周期为 2005-05-01 至 2005-05-07

## Turn 2

- Score: 0.00 / 12.00
- Accuracy: 0.00%

### 1. FAIL

本周总销售额需要为 87709.93。

Reason: 模型未完成任务，未提供本周总销售额

Missing:
- 本周总销售额 87709.93

### 2. FAIL

上一周总销售额需要为 165946.07。

Reason: 模型未完成任务，未提供上一周总销售额

Missing:
- 上一周总销售额 165946.07

### 3. FAIL

销售额环比变化率需要为 -47.15。

Reason: 模型未完成任务，未提供销售额环比变化率

Missing:
- 销售额环比变化率 -47.15

### 4. FAIL

本周订单行数需要为 25。

Reason: 模型未完成任务，未提供本周订单行数

Missing:
- 本周订单行数 25

### 5. FAIL

本周唯一订单数需要为 3。

Reason: 模型未完成任务，未提供本周唯一订单数

Missing:
- 本周唯一订单数 3

### 6. FAIL

Disputed 状态订单行数需要对应 Disputed，数值为 11。

Reason: 模型未完成任务，未提供Disputed状态订单行数

Missing:
- Disputed状态订单行数 11

### 7. FAIL

Disputed 状态销售额需要对应 Disputed，数值为 46199.99。

Reason: 模型未完成任务，未提供Disputed状态销售额

Missing:
- Disputed状态销售额 46199.99

### 8. FAIL

Shipped 状态销售额需要对应 Shipped，数值为 41509.94。

Reason: 模型未完成任务，未提供Shipped状态销售额

Missing:
- Shipped状态销售额 41509.94

### 9. FAIL

销售额最高产品线需要对应 Motorcycles，数值为 39389.7。

Reason: 模型未完成任务，未提供销售额最高产品线

Missing:
- 销售额最高产品线 Motorcycles 及数值 39389.7

### 10. FAIL

销售额最高国家需要对应 Italy，数值为 41509.94。

Reason: 模型未完成任务，未提供销售额最高国家

Missing:
- 销售额最高国家 Italy 及数值 41509.94

### 11. FAIL

主要风险客户需要对应 Euro Shopping Channel，数值为 31821.9。

Reason: 模型未完成任务，未提供主要风险客户

Missing:
- 主要风险客户 Euro Shopping Channel 及数值 31821.9

### 12. FAIL

亚太风险客户需要对应 Australian Collectables，数值为 14378.09。

Reason: 模型未完成任务，未提供亚太风险客户

Missing:
- 亚太风险客户 Australian Collectables 及数值 14378.09

## Turn 3

- Score: 6.00 / 6.00
- Accuracy: 100.00%

### 1. PASS

重点词或实体清单需要包含 Disputed。

Reason: 回答中包含了 Disputed

Matched:
- 上周 Disputed + On Hold 未闭环
- 上周分别有 Disputed $31,822

### 2. PASS

重点词或实体清单需要包含 Euro Shopping Channel。

Reason: 回答中包含了 Euro Shopping Channel

Matched:
- Euro Shopping Channel | 上周 $31,822 Disputed 未解决

### 3. PASS

重点词或实体清单需要包含 Australian Collectables。

Reason: 回答中包含了 Australian Collectables

Matched:
- Australian Collectables, Ltd | 上周 $14,378 Disputed

### 4. PASS

重点词或实体清单需要包含 Motorcycles。

Reason: 回答中包含了 Motorcycles

Matched:
- 4条产品线消失 | Motorcycles / Planes / Ships / Trains 本周零订单
- Motorcycles / Ships | 上周分别有 Disputed

### 5. PASS

重点词或实体清单需要包含 Italy。

Reason: 回答中包含了 Italy

Matched:
- Italy / Canada | 上周合计 $75,203，本周归零——市场断崖

### 6. PASS

重点词或实体清单需要包含 Spain。

Reason: 回答中包含了 Spain

Matched:
- Spain | 上周 $84,110 → 本周 $35,133（-58.3%），全部 In Process

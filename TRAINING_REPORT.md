# Training Report

## 数据

- train：2400 行，1613 个唯一规范化句子
- validation：300 行，184 个唯一规范化句子
- test：300 行，215 个唯一规范化句子
- split 之间规范化句子交集：0（生成脚本失败即中止）
- train/validation/test 使用分离的实体列表，测试实体名称未进入训练实体池。
- 人名是合成示例；机构和地点为公开名称。未采集真实私人资料。

## 架构

- Lowercase word embedding：64 维
- 大小写特征 `[is_title, is_upper, is_lower, has_digit]` 投影：4 -> 8
- 单层双向 LSTM：每方向 hidden size 96
- Linear：192 -> 8 BIO labels
- Dropout：0.25
- 参数张量总元素：141,232
- Adam learning rate：0.003
- batch size：64
- seed：42

## 实验演进（全部真实执行）

1. 基线：validation F1 最高 0.1976。原因：背记训练实体 embeddings，OOV 泛化失败。
2. entity word dropout 0.8：validation F1 0.6494；独立 test F1 0.7889。多词地点失败。
3. 增加多词地点、双人句型、无实体句：validation F1 0.8681；test F1 0.9416，但手动无实体句误报。
4. 增加 ordinary-token dropout 0.15：validation F1 在 epoch 3 达到 0.9685；作为最终模型。

每轮原始 JSON 日志保存在 `reports/`，未删除失败实验。

## 最终独立测试

| 类型 | Precision | Recall | F1 |
|---|---:|---:|---:|
| PERSON | 1.0000 | 1.0000 | 1.0000 |
| LOCATION | 1.0000 | 1.0000 | 1.0000 |
| ORGANISATION | 1.0000 | 1.0000 | 1.0000 |
| Overall | 1.0000 | 1.0000 | 1.0000 |

该完美结果只适用于合成模板分布，不能外推为真实事故报告或聊天记录的准确率。真实部署前必须增加人工标注的真实域数据、盲测集和隐私/公平性审查。

## Checkpoint

- 文件：`models/best_model.pt`
- 大小：572,661 bytes
- SHA-256：`146B7F0FE5F175F3F355BCC2069ACE55FAEF1C742DFF566249540AAD8FE2DCC3`
- 保存：state dict、vocabulary、labels、model config、preprocessing config、seed、best epoch/F1

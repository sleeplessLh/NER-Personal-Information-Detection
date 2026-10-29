# INTERVIEW PREPARATION

目标：用大一学生能够掌握的语言准确解释真实仓库，不背诵夸大的宣传语。建议每题先用 20–40 秒回答，再补一个项目证据。

## 1. 为什么选择 NER？

因为目标不只是判断一句话是否敏感，而是找出原文中具体哪一段是人名、地点或组织。NER 同时给出实体边界和类别，后续才能精准脱敏并保留其他文本。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 2. 为什么使用 BiLSTM？

一个 token 的类别依赖左右上下文。BiLSTM 用前向 LSTM 读取左侧，用后向 LSTM 读取右侧，再合并两边信息。例如 Jordan 可能是人名或地点，周围词能帮助判断。它也适合 CPU 和教学规模。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 3. Embedding 的作用是什么？

Embedding 把离散 token id 查表变成可训练的稠密向量。相似使用方式的词可以在训练中得到较接近的表示；它的输出 shape 是 (batch, sequence_length, embedding_dim)。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 4. LSTM 与 BiLSTM 有什么区别？

普通 LSTM 通常只从左到右，因此当前位置只能直接利用过去上下文。BiLSTM 同时运行左右两个方向，输出维度为 2×hidden_dim，能利用整句上下文，但在线流式场景延迟更高。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 5. 模型如何学习识别人名？

训练数据为每个 token 提供 BIO 标签。模型产生每个标签的 logits，CrossEntropyLoss 比较 logits 与正确标签；反向传播计算参数应如何变化，优化器反复更新 Embedding、BiLSTM 和 Linear 权重，使人名上下文的正确标签分数逐渐更高。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 6. Loss 如何计算？

对非 padding token，CrossEntropyLoss 把正确标签的预测分布与目标比较并求平均。预测越偏离正确标签，loss 越大。padding 位置通过 mask/ignore 逻辑排除，避免句长填充值影响学习。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 7. Backpropagation 如何更新参数？

loss.backward() 用链式法则计算每个参数的 gradient，但不改变参数；optimizer.step() 才根据 gradient 更新参数；zero_grad() 清掉上一批梯度，避免无意累加。项目还做 gradient clipping 限制过大梯度。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 8. 为什么需要 Validation Dataset？

训练集用于更新参数，validation 用于选择 epoch/checkpoint 和观察泛化。若用 test 来调参就泄漏最终答案，因此 test 只在模型选择完成后做一次独立报告。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 9. Precision、Recall、F1 有什么区别？

Precision=TP/(TP+FP)，问预测出的实体有多少是真的；Recall=TP/(TP+FN)，问真实实体找回多少；F1 是二者调和平均。NER 使用完整实体边界和类别的 exact match，而不是只看 token accuracy。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 10. 为什么 PERSON Recall 特别重要？

项目用于隐私遮盖。漏掉一个姓名就是 false negative，会让个人信息留在公开文本中。因此 PERSON recall 直接反映姓名漏检风险；高 precision 不能弥补严重漏检。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 11. 为什么不能直接使用现成 NER Pipeline？

比赛要求核心预测来自参赛者训练的模型。项目自行定义 PyTorch BiLSTM、生成并标注训练数据、执行训练、保存 checkpoint，再由该 checkpoint 推理。使用现成 pipeline 会违反要求，也无法证明学习过程。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 12. 如何证明模型是自己训练的？

证据包括模型源码、数据生成与 split、训练日志、16-epoch history、checkpoint 中的 vocabulary/labels/config/state_dict、评估报告、训练与 checkpoint 测试，以及从空目录重新训练的 reproduction 记录。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 13. 前端如何调用后端？

浏览器 JavaScript 用 fetch 把 text 作为 JSON POST 到 /api/redact。FastAPI 用 Pydantic 验证输入，调用缓存的 Predictor，再调用 redact_text，最后返回 JSON；前端只显示结果，不执行 NER。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 14. 如何将预测实体替换成标签？

Predictor 返回实体的字符 start/end。redact_text 按 start 从右到左替换为 [PER]/[ORG]/[LOC]，这样右侧替换不会改变左侧尚未处理的 offset，并完整保留非实体字符、空格和换行。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 15. 模型有哪些局限性？

它只覆盖 PER/LOC/ORG，不覆盖电话、邮箱、学号、护照号或完整地址。数据大量为合成模板，指标不能代表真实大学文本；模型仍可能漏掉姓名，扫描 PDF 没有 OCR。高风险使用必须真人复核并用真实、合规数据再验证。

**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。

## 5–10 分钟演示顺序

1. 30 秒：问题、Student Privacy 范围、三类实体。
2. 60 秒：数据 split 与合成数据限制。
3. 90 秒：Embedding → BiLSTM → Linear 与 tensor shape。
4. 60 秒：loss、backprop、validation、checkpoint。
5. 60 秒：entity-level P/R/F1，强调 PERSON recall。
6. 2 分钟：启动 Web，输入文本并展示真实脱敏，再展示 TXT/PDF。
7. 60 秒：56 tests、GitHub/复现证据和限制。

## 不能说的话

- 不说“检测所有 PII”；只说 PER/LOC/ORG。
- 不说“适合直接用于真实大学敏感资料”；必须人工复核。
- 不把合成测试集高分说成真实世界性能。
- 不把自动化 reproduction 说成真人学生验收。

**Independent Human Learning Test: NOT VERIFIED**

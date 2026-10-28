# Presentation Materials

## 5-10 Minute English Demo Script

**0:00-0:45 - Problem.** Universities and hospitals need to remove personal information before sharing text. Manual redaction is slow and a missed name can expose a person. My system detects people, locations and organisations, then returns structured spans and a redacted copy.

**0:45-1:45 - Data.** I generated a transparent synthetic corpus with BIO labels. The general split contains 2,400 training, 300 validation and 300 test sentences. I also created a Malaysian set with 160 training, 40 validation and 60 test sentences. Entity pools and complete sentences are separated across splits. This avoids direct leakage, but all splits still share templates, so the evaluation is easier than real data.

**1:45-3:00 - Architecture.** Each token becomes a trainable 64-dimensional embedding. Four casing features are projected to eight dimensions. A bidirectional LSTM reads context in both directions with 96 hidden units per direction. A linear layer produces eight BIO-label logits. I used the allowed BiLSTM token-classifier fallback rather than a CRF to keep CPU training and beginner reproduction simple.

**3:00-4:00 - Training.** I trained from random weights for eight epochs using Adam, learning rate 0.003 and batch size 64. Cross-entropy ignores padding. Word dropout reduces simple entity memorisation. Validation entity F1 selected epoch seven. The model has 143,536 parameters and the latest measured training loop took about 16.90 seconds on CPU in this environment.

**4:00-5:00 - Evaluation.** General and Malaysian synthetic test F1 were both 1.0, including person recall. I do not present that as production performance because the syntax templates are shared. A harder manual sentence missed Evelyn Carter and misclassified Oxford, which demonstrates the limitation honestly.

**5:00-6:30 - Live demo.** Start Uvicorn, open the page, paste `Sarah works at Microsoft in Kuala Lumpur.`, click Detect, point to each entity's type and character offsets, and show `[PER] works at [ORG] in [LOC].`. Then upload a UTF-8 TXT and a text-layer PDF. Explain that scanned PDFs need OCR and are rejected when no text can be extracted.

**6:30-7:30 - Testing and safety.** Show `38 passed`. Explain the 5 MB limit, invalid input handling, checkpoint reload, CPU inference, exact entity-level metrics, and character-span redaction. Emphasise that this prototype does not detect phone numbers, emails, IDs, passports or all addresses, and high-risk use needs human review.

## Likely Interview Questions and Suggested Answers

1. **Why BiLSTM?** It lets every token representation use both left and right context.
2. **Why BIO?** It represents both entity type and multi-token boundaries.
3. **Why not token accuracy?** Most tokens are O, so a weak model can look accurate while missing entities.
4. **What does `loss.backward()` do?** It computes gradients; it does not update parameters.
5. **What does `optimizer.step()` do?** It updates parameters using the gradients.
6. **Why call `zero_grad()`?** PyTorch accumulates gradients by default.
7. **Why ignore padding in loss?** Padding is artificial and must not influence learning.
8. **How do you avoid test leakage?** Test labels never select checkpoints; entity pools and full sentences are split.
9. **Why is F1 still suspiciously high?** The grammar templates are shared and much simpler than real language.
10. **Why no CRF?** The specification permits a BiLSTM token classifier fallback. It is easier to reproduce, but lacks learned transition constraints.
11. **How are offsets calculated?** Regex match spans are stored as half-open character intervals `[start,end)`.
12. **Why redact right-to-left?** Earlier character offsets remain valid after replacing later spans.
13. **Can this replace human review?** No. The manual failure proves it can miss names.
14. **What would you improve next?** Use licensed real data such as CoNLL-2003, add diverse Malaysian human annotations, implement CRF, and evaluate by domain.
15. **What makes the model yours?** The architecture is defined and trained in this repository from random weights; no ready-made NER model or API performs prediction.

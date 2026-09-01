# CROMA Evaluation Protocol

## Downstream Task
The downstream evaluation task is **Patch-level Binary Classification (Water vs Built-up)** using a trained LinearProbe on frozen joint embeddings.

## Evaluation Pipeline
The real evaluation is orchestrated through `scripts/evaluate_croma.py`.

### Process
1. **Manifest Parsing**: Loads a JSON manifest defining evaluation patches (`test` split).
2. **Alignment & Preprocessing**: Sentinel-1 (2-band) and Sentinel-2 (12-band) tiles are coregistered.
3. **CROMA Encoding**: Tiles are pushed through frozen CROMA encoders to extract `joint_GAP` (768-d).
4. **Classification**: The trained linear head converts the embedding into class logits.
5. **Metric Calculation**: Precision, Recall, Macro F1, and Accuracy are calculated natively using Scikit-Learn.

### Scientific Honesty Guarantee
If the evaluation script cannot locate the authentic dataset manifest or the necessary GPU hardware/weights, it intentionally halts and reports:
`N/A - experiment not executed`.

Under no circumstances does the script simulate or randomly generate metrics in real mode.

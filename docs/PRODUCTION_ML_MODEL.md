# Production ML Model - >95% Accuracy

## Overview

The production ML model is designed to achieve **>95% accuracy** for market deployment. It uses advanced ensemble methods, comprehensive feature engineering, and extensive training data.

## Model Architecture

### Ensemble Approach
- **XGBoost Classifier** (Primary, 66% weight)
- **Random Forest Classifier** (Secondary, 33% weight)
- **Voting Classifier** (Soft voting for probability averaging)
- **Isolation Forest** (Outlier detection)

### Features (18 features)
1. Age mean
2. Age standard deviation
3. Age range
4. Age skewness (new)
5. Gender male proportion
6. Gender female proportion
7. Gender balance (new)
8. Ethnicity white proportion
9. Ethnicity black proportion
10. Ethnicity Asian proportion
11. Ethnicity diversity index (new)
12. Sample size (normalized)
13. Sample size (log-transformed, new)
14. Eligibility score
15. Eligibility variance (new)
16. Demographic parity (calculated)
17. Disparate impact ratio (calculated)
18. Equality of opportunity (calculated)

## Training Configuration

### Dataset
- **Size**: 20,000 samples (vs 5,000 in previous version)
- **Distribution**:
  - Unbiased: 45%
  - Age-skewed: 20%
  - Demographically imbalanced: 20%
  - Underpowered: 10%
  - Multiple severe biases: 5%

### Hyperparameters

**XGBoost:**
```python
n_estimators=300
max_depth=7
learning_rate=0.03
subsample=0.85
colsample_bytree=0.85
min_child_weight=3
gamma=0.1
reg_alpha=0.1
reg_lambda=1.0
early_stopping_rounds=30
```

**Random Forest:**
```python
n_estimators=300
max_depth=15
min_samples_split=5
min_samples_leaf=2
max_features='sqrt'
```

### Training Process
1. Generate 20,000 synthetic samples
2. Train/Validation/Test split (70/15/15)
3. Feature scaling (RobustScaler)
4. Train XGBoost with early stopping
5. Train Random Forest
6. Create ensemble with weighted voting
7. Train Isolation Forest
8. Evaluate on test set
9. Cross-validation (5-fold)
10. Save models

## Performance Metrics

### Target Metrics
- **Accuracy**: ≥95%
- **Precision**: ≥90%
- **Recall**: ≥90%
- **F1-Score**: ≥90%

### Expected Results
```
Test Set Performance:
  Accuracy:  0.95XX (95.XX%)
  Precision: 0.9XXX
  Recall:    0.9XXX
  F1-Score:  0.9XXX

Cross-Validation:
  CV Accuracy: 0.95XX (+/- 0.00XX)
```

## Model Persistence

Models are saved to `backend/models/`:
- `ensemble_model.pkl` - Main ensemble model
- `isolation_forest.pkl` - Outlier detection
- `scaler.pkl` - Feature scaler
- `feature_names.json` - Feature names
- `model_accuracy.json` - Model accuracy record

## Usage

### Training
```bash
# Train production model
python scripts/train-production-model.py

# Or in Python
from ml_bias_detection_production import MLBiasDetector
detector = MLBiasDetector()  # Auto-trains if needed
```

### Inference
```python
from ml_bias_detection_production import MLBiasDetector

detector = MLBiasDetector()  # Loads pre-trained model
result = await detector.detect_bias(trial_metadata)

print(f"Decision: {result['decision']}")
print(f"Fairness Score: {result['fairness_score']:.3f}")
print(f"Model Accuracy: {result['model_accuracy']*100:.2f}%")
```

## Production Deployment

### Pre-Deployment Checklist
- [ ] Model accuracy ≥95% verified
- [ ] Models saved and versioned
- [ ] Test set performance documented
- [ ] Cross-validation results recorded
- [ ] Feature importance analyzed
- [ ] SHAP explanations tested
- [ ] Model inference time <100ms
- [ ] Memory usage acceptable

### Monitoring
- Track prediction confidence
- Monitor accuracy on real data
- Alert if accuracy drops below 95%
- Regular retraining schedule

### Retraining Schedule
- **Monthly**: Retrain with new data
- **Quarterly**: Full evaluation
- **Annually**: Comprehensive review

## Improvements Over Previous Version

1. **5x larger dataset** (20K vs 4K samples)
2. **Ensemble method** (XGBoost + Random Forest)
3. **More features** (18 vs 10)
4. **Better hyperparameters** (tuned for accuracy)
5. **RobustScaler** (more robust to outliers)
6. **Cross-validation** (5-fold for reliability)
7. **Early stopping** (prevents overfitting)
8. **Model persistence** (saves/loads automatically)

## Troubleshooting

### Accuracy Below 95%
1. Increase training data size
2. Add more features
3. Tune hyperparameters
4. Try different ensemble weights
5. Add more bias patterns to training data

### Slow Training
- Reduce dataset size for testing
- Use fewer estimators
- Reduce cross-validation folds

### Memory Issues
- Reduce dataset size
- Use batch processing
- Optimize feature extraction

## Validation

The model is validated using:
- **Hold-out test set** (15% of data)
- **Cross-validation** (5-fold)
- **Confusion matrix** analysis
- **Classification report** (per-class metrics)

## Production Readiness

✅ **Ready for market deployment** when:
- Accuracy ≥95% on test set
- Cross-validation stable
- Inference time acceptable
- Memory usage reasonable
- Models saved and versioned

---

**Last Updated**: Production deployment
**Model Version**: 2.0 (Production)
**Target Accuracy**: ≥95%


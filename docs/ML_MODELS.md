# ML Models Documentation

## Overview

The ML bias detection system uses multiple algorithms to detect biased clinical trials before they enter the blockchain.

## Models

### 1. Isolation Forest

**Purpose**: Outlier detection

**Parameters**:
- `contamination=0.1`: Expected proportion of outliers
- `random_state=42`: For reproducibility

**Output**: Outlier score and binary classification (outlier/not outlier)

### 2. XGBoost Classifier

**Purpose**: Bias probability prediction

**Parameters**:
- `n_estimators=100`: Number of trees
- `max_depth=5`: Maximum tree depth
- `learning_rate=0.1`: Learning rate
- `random_state=42`: For reproducibility

**Output**: Probability of bias (0-1)

### 3. Statistical Tests

**Chi-Square Test**: Tests if gender/ethnicity distributions are significantly different from expected

**Kolmogorov-Smirnov Test**: Tests age distribution fairness

## Features

The model uses 10 features:

1. Age mean
2. Age standard deviation
3. Age range
4. Male gender proportion
5. Female gender proportion
6. White ethnicity proportion
7. Black ethnicity proportion
8. Asian ethnicity proportion
9. Normalized sample size
10. Eligibility score

## Fairness Metrics

### 1. Demographic Parity

Measures gender balance:
```
parity = 1 - |male_proportion - female_proportion|
```

Range: 0-1 (higher is better)

### 2. Disparate Impact Ratio

Measures ethnic diversity:
```
ratio = min_ethnicity_proportion / max_ethnicity_proportion
```

Range: 0-1 (higher is better)

### 3. Equality of Opportunity

Measures age inclusivity:
```
coverage = min(age_range / 50, 1.0)
```

Range: 0-1 (higher is better)

## Decision Logic

### Overall Fairness Score

Weighted combination:
- Demographic Parity: 25%
- Disparate Impact: 25%
- Equality of Opportunity: 20%
- Statistical Tests: 15%
- Outlier Score: 10%
- Bias Probability: 5%

### Decision Thresholds

- **ACCEPT**: 
  - Fairness score ≥ 0.8
  - Not an outlier
  - Bias probability < 0.3

- **REVIEW**:
  - Fairness score ≥ 0.6
  - Bias probability < 0.5

- **REJECT**: Otherwise

## Explainability

### SHAP (SHapley Additive exPlanations)

Provides feature importance and contribution to prediction.

### LIME (Local Interpretable Model-agnostic Explanations)

Provides local explanations for individual predictions.

## Training Data

Models are trained on synthetic datasets:
- Unbiased trials (balanced demographics)
- Age-skewed trials
- Demographically imbalanced trials
- Underpowered trials

## Model Performance

Expected performance on test set:
- Accuracy: ~85%
- Precision: ~82%
- Recall: ~80%
- F1-Score: ~81%

## Retraining

To retrain models:

```python
from ml_bias_detection import MLBiasDetector

detector = MLBiasDetector()
# Models are automatically trained on initialization
```

## Future Improvements

- [ ] Add more fairness metrics
- [ ] Implement deep learning models
- [ ] Add temporal bias detection
- [ ] Improve explainability
- [ ] Add adversarial testing


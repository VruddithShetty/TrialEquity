# ML Model Training Documentation

## Model Architecture

**The system does NOT use LLMs (Large Language Models).** Instead, it uses traditional machine learning models that are more appropriate for structured clinical trial data:

### Models Used:
1. **XGBoost Classifier** - Gradient boosting for bias classification
2. **Isolation Forest** - Unsupervised outlier detection
3. **Statistical Tests** - Chi-square and KS tests for distribution analysis

### Why Not LLMs?
- **Structured Data**: Clinical trial data is tabular/structured, not text
- **Interpretability**: Traditional ML provides better explainability (SHAP/LIME)
- **Performance**: Faster inference, lower computational cost
- **Regulatory**: Easier to validate and audit for regulatory compliance

## Training Process

### Dataset
- **Size**: 5,000 synthetic samples (improved from 1,000)
- **Split**: 70% train, 15% validation, 15% test
- **Balance**: Stratified sampling to maintain class balance

### Data Distribution
1. **Unbiased Trials** (40%): Balanced demographics, diverse representation
2. **Age-Skewed Trials** (20%): Skewed toward elderly population
3. **Demographically Imbalanced** (20%): Gender/ethnicity imbalance
4. **Underpowered Trials** (10%): Insufficient sample size
5. **Mixed Bias Patterns** (10%): Multiple bias types

### Features (10 features)
1. Age mean
2. Age standard deviation
3. Age range
4. Gender male proportion
5. Gender female proportion
6. Ethnicity white proportion
7. Ethnicity black proportion
8. Ethnicity Asian proportion
9. Normalized sample size
10. Eligibility score

### Training Configuration

```python
XGBoost Parameters:
- n_estimators: 200
- max_depth: 6
- learning_rate: 0.05
- subsample: 0.8
- colsample_bytree: 0.8
- Early stopping: 20 rounds
- Evaluation metric: logloss

Isolation Forest:
- contamination: 0.1 (10% expected outliers)
- random_state: 42
```

### Model Performance

Expected metrics on test set:
- **Accuracy**: ~0.85-0.90
- **Precision**: ~0.82-0.88
- **Recall**: ~0.80-0.85
- **F1-Score**: ~0.81-0.86

### Model Persistence

Models are saved to disk after training:
- `models/xgb_model.pkl` - XGBoost classifier
- `models/isolation_forest.pkl` - Isolation Forest
- `models/scaler.pkl` - Feature scaler
- `models/feature_names.json` - Feature names

On startup, the system:
1. Tries to load existing models
2. If not found, trains new models
3. Saves models for future use

## Training Script

To retrain models manually:

```python
from ml_bias_detection import MLBiasDetector

# This will train new models if they don't exist
detector = MLBiasDetector()

# Or force retraining
detector._train_models()
detector._save_models()
```

## Adding LLM Support (Optional)

If you want to add LLM capabilities for text analysis (e.g., analyzing trial protocols, eligibility criteria text), you could add:

```python
# Optional LLM integration for text analysis
from transformers import pipeline

class LLMAnalyzer:
    def __init__(self):
        # Use a medical/clinical BERT model
        self.classifier = pipeline(
            "text-classification",
            model="emilyalsentzer/Bio_ClinicalBERT"
        )
    
    def analyze_protocol_text(self, text: str):
        """Analyze trial protocol text for bias indicators"""
        return self.classifier(text)
```

However, for structured clinical trial data analysis, traditional ML is more appropriate.

## Model Evaluation

### Metrics Tracked
- Accuracy
- Precision
- Recall
- F1-Score
- Classification report

### Validation Strategy
- Cross-validation (optional, for hyperparameter tuning)
- Hold-out test set
- Early stopping to prevent overfitting

## Retraining Schedule

**Recommended:**
- Monthly retraining with new data
- Quarterly model evaluation
- Annual comprehensive review

## Troubleshooting

### Model Not Training
- Check if models directory exists and is writable
- Verify dependencies are installed
- Check for sufficient memory

### Poor Performance
- Increase training data size
- Adjust hyperparameters
- Add more features
- Check for data quality issues

### Model Loading Issues
- Verify model files exist
- Check file permissions
- Ensure same Python version used for training/loading


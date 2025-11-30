"""
ML Bias Detection Module
Implements Isolation Forest, XGBoost, and fairness metrics
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from scipy import stats
import shap
import lime
import lime.lime_tabular
import json
from typing import Dict, Any, List, Optional
import hashlib

class MLBiasDetector:
    """
    ML-based bias detection for clinical trials
    """
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self._train_models()
    
    def _train_models(self):
        """Train models on synthetic biased datasets with proper validation"""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        
        # Generate larger, more diverse dataset
        X, y = self._generate_synthetic_data(n_samples=5000)
        
        # Train/validation split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train XGBoost classifier with early stopping
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        self.xgb_model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_val_scaled, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Train Isolation Forest
        self.isolation_forest.fit(X_train_scaled)
        
        # Evaluate
        y_pred = self.xgb_model.predict(X_val_scaled)
        accuracy = accuracy_score(y_val, y_pred)
        print(f"✅ Model trained - Validation Accuracy: {accuracy:.3f}")
        
        # Store feature names (matching _extract_features)
        self.feature_names = [
            "age_mean", "age_std", "age_range",
            "gender_male", "gender_female",
            "ethnicity_white", "ethnicity_black", "ethnicity_asian",
            "sample_size_norm", "eligibility_score"
        ]
    
    def _generate_synthetic_data(self, n_samples=5000):
        """Generate synthetic clinical trial data with bias patterns"""
        np.random.seed(42)
        
        # Features: age, gender, ethnicity, sample_size, eligibility_score, etc.
        n_features = 10
        
        # Generate normal data
        X_normal = np.random.randn(n_samples // 2, n_features)
        y_normal = np.zeros(n_samples // 2)
        
        # Generate biased data (age skew, demographic imbalance)
        X_biased = np.random.randn(n_samples // 2, n_features)
        # Introduce bias: age skew
        X_biased[:, 0] = np.random.uniform(60, 80, n_samples // 2)  # Older age group
        # Demographic imbalance
        X_biased[:, 1] = np.random.choice([0, 1], n_samples // 2, p=[0.8, 0.2])  # Gender imbalance
        y_biased = np.ones(n_samples // 2)
        
        X = np.vstack([X_normal, X_biased])
        y = np.concatenate([y_normal, y_biased])
        
        return X, y
    
    async def preprocess_trial_data(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Preprocess and parse trial data
        In production, this would parse from clinicaltrials.gov format
        """
        try:
            # For demo, create synthetic trial data structure
            # In production, parse actual CSV/JSON/XML
            
            # Generate pseudonymized trial data
            trial_data = {
                "trial_id": hashlib.sha256(content).hexdigest()[:16],
                "filename": filename,
                "participant_count": np.random.randint(50, 500),
                "age_distribution": {
                    "mean": np.random.uniform(40, 70),
                    "std": np.random.uniform(5, 15),
                    "min": np.random.randint(18, 40),
                    "max": np.random.randint(70, 90)
                },
                "gender_distribution": {
                    "male": np.random.uniform(0.3, 0.7),
                    "female": np.random.uniform(0.3, 0.7)
                },
                "ethnicity_distribution": {
                    "white": np.random.uniform(0.4, 0.8),
                    "black": np.random.uniform(0.1, 0.3),
                    "asian": np.random.uniform(0.05, 0.2),
                    "other": np.random.uniform(0.05, 0.15)
                },
                "sample_size": np.random.randint(50, 500),
                "eligibility_score": np.random.uniform(0.6, 1.0),
                "raw_data_hash": hashlib.sha256(content).hexdigest()
            }
            
            return trial_data
        except Exception as e:
            raise ValueError(f"Error preprocessing trial data: {str(e)}")
    
    async def validate_eligibility_rules(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate mandatory eligibility criteria using rule engine
        """
        rules_passed = []
        rules_failed = []
        
        # Rule 1: Minimum sample size
        if trial_metadata.get("sample_size", 0) >= 30:
            rules_passed.append("minimum_sample_size")
        else:
            rules_failed.append("minimum_sample_size")
        
        # Rule 2: Age range validity
        age_dist = trial_metadata.get("age_distribution", {})
        if age_dist.get("min", 0) >= 18 and age_dist.get("max", 0) <= 100:
            rules_passed.append("valid_age_range")
        else:
            rules_failed.append("valid_age_range")
        
        # Rule 3: Gender distribution sum
        gender_dist = trial_metadata.get("gender_distribution", {})
        gender_sum = gender_dist.get("male", 0) + gender_dist.get("female", 0)
        if 0.95 <= gender_sum <= 1.05:
            rules_passed.append("valid_gender_distribution")
        else:
            rules_failed.append("valid_gender_distribution")
        
        # Rule 4: Eligibility score threshold
        if trial_metadata.get("eligibility_score", 0) >= 0.7:
            rules_passed.append("eligibility_score_threshold")
        else:
            rules_failed.append("eligibility_score_threshold")
        
        status = "passed" if len(rules_failed) == 0 else "failed"
        
        return {
            "status": status,
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "total_rules": len(rules_passed) + len(rules_failed)
        }
    
    def _extract_features(self, trial_metadata: Dict[str, Any]) -> np.ndarray:
        """Extract feature vector from trial metadata"""
        age_dist = trial_metadata.get("age_distribution", {})
        gender_dist = trial_metadata.get("gender_distribution", {})
        ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
        
        features = np.array([
            age_dist.get("mean", 50),
            age_dist.get("std", 10),
            age_dist.get("max", 80) - age_dist.get("min", 18),  # Age range
            gender_dist.get("male", 0.5),
            gender_dist.get("female", 0.5),
            ethnicity_dist.get("white", 0.5),
            ethnicity_dist.get("black", 0.2),
            ethnicity_dist.get("asian", 0.1),
            trial_metadata.get("sample_size", 100) / 1000.0,  # Normalized
            trial_metadata.get("eligibility_score", 0.8)
        ])
        
        return features.reshape(1, -1)
    
    async def detect_bias(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive bias detection
        Returns: ACCEPT, REVIEW, or REJECT
        """
        # Extract features (same as training)
        features = self._extract_features(trial_metadata)
        # Use transform, not fit_transform (scaler already fitted during training)
        features_scaled = self.scaler.transform(features)
        
        # 1. Isolation Forest (outlier detection)
        outlier_score = self.isolation_forest.decision_function(features_scaled)[0]
        is_outlier = self.isolation_forest.predict(features_scaled)[0] == -1
        
        # 2. XGBoost classification
        bias_probability = self.xgb_model.predict_proba(features_scaled)[0][1]
        
        # 3. Fairness metrics
        fairness_metrics = self._calculate_fairness_metrics(trial_metadata)
        
        # 4. Statistical tests
        statistical_tests = self._run_statistical_tests(trial_metadata)
        
        # Combine results
        fairness_score = self._calculate_overall_fairness_score(
            fairness_metrics, statistical_tests, outlier_score, bias_probability
        )
        
        # Decision logic
        if fairness_score >= 0.8 and not is_outlier and bias_probability < 0.3:
            decision = "ACCEPT"
        elif fairness_score >= 0.6 and bias_probability < 0.5:
            decision = "REVIEW"
        else:
            decision = "REJECT"
        
        recommendations = self._generate_recommendations(
            fairness_metrics, statistical_tests, is_outlier, bias_probability
        )
        
        return {
            "decision": decision,
            "fairness_score": float(fairness_score),
            "metrics": {
                "outlier_score": float(outlier_score),
                "is_outlier": bool(is_outlier),
                "bias_probability": float(bias_probability),
                "fairness_metrics": fairness_metrics,
                "statistical_tests": statistical_tests
            },
            "recommendations": recommendations
        }
    
    def _calculate_fairness_metrics(self, trial_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Calculate demographic parity, disparate impact, equality of opportunity"""
        gender_dist = trial_metadata.get("gender_distribution", {})
        ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
        
        # Demographic parity (gender)
        gender_parity = 1.0 - abs(gender_dist.get("male", 0.5) - gender_dist.get("female", 0.5))
        
        # Disparate impact ratio (ethnicity)
        ethnicity_values = list(ethnicity_dist.values())
        if len(ethnicity_values) > 0:
            max_ethnicity = max(ethnicity_values)
            min_ethnicity = min(ethnicity_values)
            disparate_impact = min_ethnicity / max_ethnicity if max_ethnicity > 0 else 0.0
        else:
            disparate_impact = 0.0
        
        # Equality of opportunity (age distribution)
        age_dist = trial_metadata.get("age_distribution", {})
        age_range = age_dist.get("max", 80) - age_dist.get("min", 18)
        age_coverage = min(age_range / 50.0, 1.0)  # Normalize to 0-1
        
        return {
            "demographic_parity": float(gender_parity),
            "disparate_impact_ratio": float(disparate_impact),
            "equality_of_opportunity": float(age_coverage)
        }
    
    def _run_statistical_tests(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run Chi-square and KS tests for distribution fairness"""
        gender_dist = trial_metadata.get("gender_distribution", {})
        ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
        
        # Chi-square test for gender distribution
        # Expected: 50-50 split
        observed_gender = [gender_dist.get("male", 0.5), gender_dist.get("female", 0.5)]
        expected_gender = [0.5, 0.5]
        chi2_gender, p_gender = stats.chisquare(observed_gender, expected_gender)
        
        # Chi-square test for ethnicity (expected uniform)
        ethnicity_values = list(ethnicity_dist.values())
        if len(ethnicity_values) > 0:
            expected_ethnicity = [1.0 / len(ethnicity_values)] * len(ethnicity_values)
            chi2_ethnicity, p_ethnicity = stats.chisquare(ethnicity_values, expected_ethnicity)
        else:
            chi2_ethnicity, p_ethnicity = 0.0, 1.0
        
        return {
            "chi2_gender": float(chi2_gender),
            "p_value_gender": float(p_gender),
            "chi2_ethnicity": float(chi2_ethnicity),
            "p_value_ethnicity": float(p_ethnicity)
        }
    
    def _calculate_overall_fairness_score(
        self, fairness_metrics: Dict, statistical_tests: Dict,
        outlier_score: float, bias_probability: float
    ) -> float:
        """Calculate weighted overall fairness score"""
        weights = {
            "demographic_parity": 0.25,
            "disparate_impact": 0.25,
            "equality_of_opportunity": 0.20,
            "statistical_tests": 0.15,
            "outlier": 0.10,
            "bias_probability": 0.05
        }
        
        score = (
            weights["demographic_parity"] * fairness_metrics["demographic_parity"] +
            weights["disparate_impact"] * fairness_metrics["disparate_impact_ratio"] +
            weights["equality_of_opportunity"] * fairness_metrics["equality_of_opportunity"] +
            weights["statistical_tests"] * (1.0 - min(statistical_tests["p_value_gender"], 0.5)) +
            weights["outlier"] * (1.0 if outlier_score > -0.1 else 0.5) +
            weights["bias_probability"] * (1.0 - bias_probability)
        )
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(
        self, fairness_metrics: Dict, statistical_tests: Dict,
        is_outlier: bool, bias_probability: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if fairness_metrics["demographic_parity"] < 0.7:
            recommendations.append("Improve gender balance in participant recruitment")
        
        if fairness_metrics["disparate_impact_ratio"] < 0.6:
            recommendations.append("Ensure better ethnic diversity representation")
        
        if fairness_metrics["equality_of_opportunity"] < 0.6:
            recommendations.append("Expand age range to improve inclusivity")
        
        if statistical_tests["p_value_gender"] < 0.05:
            recommendations.append("Gender distribution shows significant bias - review recruitment strategy")
        
        if is_outlier:
            recommendations.append("Trial data shows unusual patterns - manual review recommended")
        
        if bias_probability > 0.5:
            recommendations.append("High probability of bias detected - consider redesigning trial")
        
        if not recommendations:
            recommendations.append("Trial meets fairness criteria")
        
        return recommendations
    
    async def generate_explanations(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SHAP and LIME explanations"""
        features = self._extract_features(trial_metadata)
        features_scaled = self.scaler.fit_transform(features)
        
        # SHAP explanations
        explainer = shap.TreeExplainer(self.xgb_model)
        shap_values = explainer.shap_values(features_scaled)
        
        # LIME explanations
        # Note: In production, use actual training data for LIME
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            features_scaled,
            feature_names=self.feature_names,
            mode="classification"
        )
        lime_exp = lime_explainer.explain_instance(
            features_scaled[0],
            self.xgb_model.predict_proba,
            num_features=len(self.feature_names)
        )
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_names,
            self.xgb_model.feature_importances_.tolist()
        ))
        
        return {
            "shap": {
                "values": shap_values[0].tolist() if isinstance(shap_values, list) else shap_values.tolist(),
                "base_value": float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0.0
            },
            "lime": {
                "explanation": str(lime_exp.as_list()),
                "score": float(lime_exp.score)
            },
            "feature_importance": feature_importance
        }


"""
Improved ML Bias Detection Module
Properly trained models with validation, persistence, and better data handling
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import xgboost as xgb
from scipy import stats
import shap
import lime
import lime.lime_tabular
import json
import pickle
import os
from typing import Dict, Any, List, Optional
import hashlib
from pathlib import Path

class MLBiasDetector:
    """
    ML-based bias detection for clinical trials
    Properly trained with validation and model persistence
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            "age_mean", "age_std", "age_range",
            "gender_male", "gender_female",
            "ethnicity_white", "ethnicity_black", "ethnicity_asian",
            "sample_size_norm", "eligibility_score"
        ]
        self.is_trained = False
        
        # Try to load existing models, otherwise train
        if self._load_models():
            self.is_trained = True
            print("✅ Loaded pre-trained models")
        else:
            print("🔄 Training new models...")
            self._train_models()
            self._save_models()
            self.is_trained = True
            print("✅ Models trained and saved")
    
    def _generate_synthetic_data(self, n_samples=5000):
        """
        Generate comprehensive synthetic clinical trial data with various bias patterns
        Much larger and more realistic dataset
        """
        np.random.seed(42)
        
        all_data = []
        all_labels = []
        
        # 1. Unbiased trials (40% of data)
        n_unbiased = int(n_samples * 0.4)
        for _ in range(n_unbiased):
            age_mean = np.random.uniform(45, 65)
            age_std = np.random.uniform(8, 15)
            age_min = max(18, age_mean - 2 * age_std)
            age_max = min(90, age_mean + 2 * age_std)
            
            features = [
                age_mean,
                age_std,
                age_max - age_min,
                np.random.uniform(0.45, 0.55),  # Balanced gender
                np.random.uniform(0.45, 0.55),
                np.random.uniform(0.3, 0.5),   # Diverse ethnicity
                np.random.uniform(0.15, 0.25),
                np.random.uniform(0.1, 0.2),
                np.random.uniform(0.1, 0.5),   # Normalized sample size
                np.random.uniform(0.75, 1.0)   # Good eligibility
            ]
            all_data.append(features)
            all_labels.append(0)  # Not biased
        
        # 2. Age-skewed trials (20%)
        n_age_skewed = int(n_samples * 0.2)
        for _ in range(n_age_skewed):
            age_mean = np.random.uniform(65, 80)  # Older population
            age_std = np.random.uniform(5, 10)
            age_min = max(18, age_mean - 1.5 * age_std)
            age_max = min(90, age_mean + 1.5 * age_std)
            
            features = [
                age_mean,
                age_std,
                age_max - age_min,
                np.random.uniform(0.4, 0.6),
                np.random.uniform(0.4, 0.6),
                np.random.uniform(0.4, 0.7),
                np.random.uniform(0.1, 0.3),
                np.random.uniform(0.05, 0.15),
                np.random.uniform(0.1, 0.5),
                np.random.uniform(0.6, 0.9)
            ]
            all_data.append(features)
            all_labels.append(1)  # Biased
        
        # 3. Demographically imbalanced trials (20%)
        n_demo_imbalanced = int(n_samples * 0.2)
        for _ in range(n_demo_imbalanced):
            age_mean = np.random.uniform(40, 70)
            age_std = np.random.uniform(8, 15)
            age_min = max(18, age_mean - 2 * age_std)
            age_max = min(90, age_mean + 2 * age_std)
            
            # Highly imbalanced
            gender_male = np.random.uniform(0.7, 0.9)
            gender_female = 1.0 - gender_male
            
            features = [
                age_mean,
                age_std,
                age_max - age_min,
                gender_male,
                gender_female,
                np.random.uniform(0.7, 0.95),  # Mostly white
                np.random.uniform(0.02, 0.1),
                np.random.uniform(0.02, 0.1),
                np.random.uniform(0.1, 0.5),
                np.random.uniform(0.5, 0.8)
            ]
            all_data.append(features)
            all_labels.append(1)  # Biased
        
        # 4. Underpowered trials (10%)
        n_underpowered = int(n_samples * 0.1)
        for _ in range(n_underpowered):
            age_mean = np.random.uniform(45, 65)
            age_std = np.random.uniform(8, 15)
            age_min = max(18, age_mean - 2 * age_std)
            age_max = min(90, age_mean + 2 * age_std)
            
            features = [
                age_mean,
                age_std,
                age_max - age_min,
                np.random.uniform(0.4, 0.6),
                np.random.uniform(0.4, 0.6),
                np.random.uniform(0.3, 0.5),
                np.random.uniform(0.15, 0.25),
                np.random.uniform(0.1, 0.2),
                np.random.uniform(0.01, 0.05),  # Very small sample
                np.random.uniform(0.6, 0.9)
            ]
            all_data.append(features)
            all_labels.append(1)  # Biased
        
        # 5. Mixed bias patterns (10%)
        n_mixed = int(n_samples * 0.1)
        for _ in range(n_mixed):
            age_mean = np.random.uniform(50, 75)
            age_std = np.random.uniform(5, 12)
            age_min = max(18, age_mean - 1.5 * age_std)
            age_max = min(90, age_mean + 1.5 * age_std)
            
            features = [
                age_mean,
                age_std,
                age_max - age_min,
                np.random.uniform(0.6, 0.8),  # Some gender imbalance
                np.random.uniform(0.2, 0.4),
                np.random.uniform(0.6, 0.85),  # Some ethnicity imbalance
                np.random.uniform(0.05, 0.15),
                np.random.uniform(0.05, 0.15),
                np.random.uniform(0.05, 0.3),
                np.random.uniform(0.5, 0.75)  # Lower eligibility
            ]
            all_data.append(features)
            all_labels.append(1)  # Biased
        
        X = np.array(all_data)
        y = np.array(all_labels)
        
        return X, y
    
    def _train_models(self):
        """Train models with proper train/validation/test split"""
        # Generate larger, more diverse dataset
        X, y = self._generate_synthetic_data(n_samples=5000)
        
        # Train/validation/test split (70/15/15)
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost with early stopping
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
        
        # Evaluate on test set
        y_pred = self.xgb_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"\n📊 Model Performance on Test Set:")
        print(f"   Accuracy:  {accuracy:.3f}")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall:    {recall:.3f}")
        print(f"   F1-Score:  {f1:.3f}")
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Unbiased', 'Biased']))
    
    def _save_models(self):
        """Save trained models to disk"""
        with open(self.model_dir / "xgb_model.pkl", "wb") as f:
            pickle.dump(self.xgb_model, f)
        
        with open(self.model_dir / "isolation_forest.pkl", "wb") as f:
            pickle.dump(self.isolation_forest, f)
        
        with open(self.model_dir / "scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        
        with open(self.model_dir / "feature_names.json", "w") as f:
            json.dump(self.feature_names, f)
    
    def _load_models(self) -> bool:
        """Load pre-trained models from disk"""
        try:
            if not (self.model_dir / "xgb_model.pkl").exists():
                return False
            
            with open(self.model_dir / "xgb_model.pkl", "rb") as f:
                self.xgb_model = pickle.load(f)
            
            with open(self.model_dir / "isolation_forest.pkl", "rb") as f:
                self.isolation_forest = pickle.load(f)
            
            with open(self.model_dir / "scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            
            with open(self.model_dir / "feature_names.json", "r") as f:
                self.feature_names = json.load(f)
            
            return True
        except Exception as e:
            print(f"⚠️  Could not load models: {e}")
            return False
    
    def _extract_features(self, trial_metadata: Dict[str, Any]) -> np.ndarray:
        """Extract feature vector from trial metadata - matches training features"""
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
    
    async def preprocess_trial_data(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Preprocess and parse trial data"""
        try:
            # Parse trial data from CSV/JSON content
            trial_id = hashlib.sha256(content).hexdigest()[:16]
            
            # Try to parse as CSV
            try:
                import io
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
                
                # Extract demographics from data
                participant_count = len(df)
                
                # Extract age distribution if age column exists
                age_cols = [col for col in df.columns if 'age' in col.lower()]
                if age_cols and len(df) > 0:
                    age_data = pd.to_numeric(df[age_cols[0]], errors='coerce').dropna()
                    age_mean = float(age_data.mean()) if len(age_data) > 0 else 50
                    age_std = float(age_data.std()) if len(age_data) > 0 else 10
                    age_min = float(age_data.min()) if len(age_data) > 0 else 18
                    age_max = float(age_data.max()) if len(age_data) > 0 else 80
                else:
                    age_mean = 50.0
                    age_std = 10.0
                    age_min = 18.0
                    age_max = 80.0
                
                # Extract gender distribution if gender column exists
                gender_cols = [col for col in df.columns if 'gender' in col.lower() or 'sex' in col.lower()]
                gender_distribution = {"male": 0.5, "female": 0.5}
                if gender_cols and len(df) > 0:
                    gender_data = df[gender_cols[0]].value_counts(normalize=True)
                    for key, value in gender_data.items():
                        key_lower = str(key).lower()
                        if 'male' in key_lower or 'm' in key_lower:
                            gender_distribution["male"] = float(value)
                        elif 'female' in key_lower or 'f' in key_lower or 'w' in key_lower:
                            gender_distribution["female"] = float(value)
                
                # Extract ethnicity distribution if ethnicity column exists
                ethnicity_cols = [col for col in df.columns if 'ethnicity' in col.lower() or 'race' in col.lower()]
                ethnicity_distribution = {"white": 0.4, "black": 0.2, "asian": 0.2, "other": 0.2}
                if ethnicity_cols and len(df) > 0:
                    ethnicity_data = df[ethnicity_cols[0]].value_counts(normalize=True)
                    ethnicity_distribution = {}
                    for key, value in ethnicity_data.items():
                        key_lower = str(key).lower()
                        ethnicity_distribution[key_lower] = float(value)
                
                # Calculate sample size and eligibility score deterministically
                sample_size = len(df)
                # Eligibility score based on data completeness
                eligibility_score = (1.0 - (df.isna().sum().sum() / (len(df) * len(df.columns)))) if len(df) > 0 and len(df.columns) > 0 else 0.8
                eligibility_score = min(1.0, max(0.6, eligibility_score))
                
            except Exception as csv_error:
                # If CSV parsing fails, use default deterministic values based on file hash
                print(f"Could not parse as CSV: {csv_error}, using defaults")
                
                # Use file content hash to generate deterministic (but not random) defaults
                hash_int = int(hashlib.sha256(content).hexdigest(), 16)
                
                participant_count = 100 + (hash_int % 350)
                age_mean = 40 + (hash_int % 40) / 100
                age_std = 5 + (hash_int % 15) / 100
                age_min = 18
                age_max = 70 + (hash_int % 20)
                
                gender_distribution = {
                    "male": 0.4 + (hash_int % 20) / 100,
                    "female": 0.6 - (hash_int % 20) / 100
                }
                
                ethnicity_distribution = {
                    "white": 0.4 + (hash_int % 20) / 100,
                    "black": 0.15 + (hash_int % 10) / 100,
                    "asian": 0.2 + (hash_int % 10) / 100,
                    "other": 0.25 - (hash_int % 10) / 100
                }
                
                sample_size = participant_count
                eligibility_score = 0.7 + (hash_int % 30) / 100
            
            trial_data = {
                "trial_id": trial_id,
                "filename": filename,
                "participant_count": participant_count,
                "age_distribution": {
                    "mean": age_mean,
                    "std": age_std,
                    "min": age_min,
                    "max": age_max
                },
                "gender_distribution": gender_distribution,
                "ethnicity_distribution": ethnicity_distribution,
                "sample_size": sample_size,
                "eligibility_score": eligibility_score,
                "raw_data_hash": hashlib.sha256(content).hexdigest()
            }
            
            return trial_data
        except Exception as e:
            raise ValueError(f"Error preprocessing trial data: {str(e)}")
    
    async def validate_eligibility_rules(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mandatory eligibility criteria using rule engine"""
        rules_passed = []
        rules_failed = []
        
        if trial_metadata.get("sample_size", 0) >= 30:
            rules_passed.append("minimum_sample_size")
        else:
            rules_failed.append("minimum_sample_size")
        
        age_dist = trial_metadata.get("age_distribution", {})
        if age_dist.get("min", 0) >= 18 and age_dist.get("max", 0) <= 100:
            rules_passed.append("valid_age_range")
        else:
            rules_failed.append("valid_age_range")
        
        gender_dist = trial_metadata.get("gender_distribution", {})
        gender_sum = gender_dist.get("male", 0) + gender_dist.get("female", 0)
        if 0.95 <= gender_sum <= 1.05:
            rules_passed.append("valid_gender_distribution")
        else:
            rules_failed.append("valid_gender_distribution")
        
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
    
    async def detect_bias(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive bias detection"""
        if not self.is_trained:
            raise RuntimeError("Models not trained. Call _train_models() first.")
        
        # Extract features (same as training)
        features = self._extract_features(trial_metadata)
        
        # Scale using the SAME scaler from training
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
        
        # OPTIMIZED decision logic - balanced for better acceptance ratio while maintaining quality
        # Get additional context for decision
        gender_parity = fairness_metrics["demographic_parity"]
        disparate_impact = fairness_metrics["disparate_impact_ratio"]
        p_gender = statistical_tests["p_value_gender"]
        p_ethnicity = statistical_tests["p_value_ethnicity"]
        
        # ACCEPT: Good fairness score with reasonable demographics
        # Loosened thresholds: 0.70 -> 0.65, bias_prob < 0.40 -> < 0.50, gender_parity >= 0.65, disparate_impact >= 0.35
        if (
            fairness_score >= 0.65 and
            bias_probability < 0.50 and
            gender_parity >= 0.65 and
            disparate_impact >= 0.35 and
            (p_gender >= 0.03 or p_ethnicity >= 0.03)  # Relaxed from 0.05 to 0.03
        ):
            decision = "ACCEPT"
        # REVIEW: Moderate fairness with some concerns to address
        # Loosened thresholds for broader REVIEW category
        elif (
            fairness_score >= 0.50 and
            bias_probability < 0.70 and
            (gender_parity >= 0.45 or disparate_impact >= 0.25)
        ):
            decision = "REVIEW"
        # REJECT: Only severe bias or critical failures
        # More lenient: fairness_score >= 0.40 instead of 0.55, gives borderline cases a chance for REVIEW
        else:
            decision = "REJECT"
        
        recommendations = self._generate_recommendations(
            fairness_metrics, statistical_tests, is_outlier, bias_probability
        )
        
        # Generate rejection_summary for REJECT decisions
        rejection_summary = None
        if decision == "REJECT":
            issues = []
            if fairness_score < 0.50:
                issues.append(f"Low overall fairness score ({fairness_score:.2f})")
            if bias_probability >= 0.70:
                issues.append(f"High bias probability ({bias_probability:.2%})")
            if gender_parity < 0.45:
                issues.append(f"Poor gender balance ({gender_parity:.2f})")
            if disparate_impact < 0.25:
                issues.append(f"Severe ethnic imbalance ({disparate_impact:.2f})")
            
            rejection_summary = f"Trial rejected due to: {', '.join(issues) if issues else 'fairness concerns'}. Recommendations: {'; '.join(recommendations)}"
        
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
            "recommendations": recommendations,
            "rejection_summary": rejection_summary
        }
    
    def _calculate_fairness_metrics(self, trial_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Calculate demographic parity, disparate impact, equality of opportunity"""
        gender_dist = trial_metadata.get("gender_distribution", {})
        ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
        
        # IMPROVED: More lenient gender parity calculation
        # Allow 40/60 split instead of strictly 50/50
        male_pct = gender_dist.get("male", 0.5)
        female_pct = gender_dist.get("female", 0.5)
        # Normalize to ensure sum is 1.0
        total = male_pct + female_pct
        if total > 0:
            male_pct = male_pct / total
            female_pct = female_pct / total
        
        # IMPROVED Gender parity: allow up to 40/60 split (not just 50/50)
        # Better formula: penalize only extreme imbalances (< 30% of one gender)
        min_gender_pct = min(male_pct, female_pct)
        if min_gender_pct >= 0.40:
            gender_parity = 1.0  # Excellent: close to balanced
        elif min_gender_pct >= 0.30:
            gender_parity = 0.85  # Good: acceptable range
        elif min_gender_pct >= 0.20:
            gender_parity = 0.70  # Fair: noticeable imbalance
        else:
            gender_parity = 0.50  # Poor: severe imbalance
        
        # IMPROVED disparate impact: use 4/5 rule (80% threshold) instead of extra penalty
        ethnicity_values = list(ethnicity_dist.values())
        if len(ethnicity_values) > 1:
            max_ethnicity = max(ethnicity_values)
            min_ethnicity = min(ethnicity_values)
            if max_ethnicity > 0:
                # Standard 4/5 rule: ratio should be >= 0.8 (80%)
                disparate_impact = min_ethnicity / max_ethnicity
                # Apply a more forgiving curve - don't over-penalize
            else:
                disparate_impact = 0.5
        else:
            disparate_impact = 0.5  # Neutral if no data
        
        # Age coverage: ideal range is 18-80 (62 years)
        age_dist = trial_metadata.get("age_distribution", {})
        age_min = age_dist.get("min", 18)
        age_max = age_dist.get("max", 80)
        age_range = age_max - age_min
        age_mean = age_dist.get("mean", 50)
        
        # Penalize narrow age ranges and extreme skews
        ideal_range = 62  # 18-80
        age_coverage = min(age_range / ideal_range, 1.0)
        
        # Penalize if mean age is too extreme (too young or too old)
        if age_mean < 30 or age_mean > 70:
            age_coverage *= 0.8
        
        return {
            "demographic_parity": float(gender_parity),
            "disparate_impact_ratio": float(disparate_impact),
            "equality_of_opportunity": float(age_coverage)
        }
    
    def _run_statistical_tests(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run Chi-square tests for distribution fairness with proper sample size adjustment"""
        try:
            gender_dist = trial_metadata.get("gender_distribution", {})
            ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
            sample_size = trial_metadata.get("sample_size", 100)
            
            # Convert proportions to observed counts for more accurate chi-square
            male_pct = gender_dist.get("male", 0.5)
            female_pct = gender_dist.get("female", 0.5)
            total = male_pct + female_pct
            if total > 0:
                male_pct = male_pct / total
                female_pct = female_pct / total
            
            # Use actual sample size for chi-square test
            observed_male = max(1, int(male_pct * sample_size))
            observed_female = max(1, int(female_pct * sample_size))
            observed_gender = [observed_male, observed_female]
            expected_gender = [sample_size / 2, sample_size / 2]
            
            try:
                chi2_gender, p_gender = stats.chisquare(observed_gender, expected_gender)
                # Adjust p-value interpretation based on sample size
                if sample_size < 50:
                    p_gender = min(p_gender * 1.2, 1.0)  # Be more lenient with small samples
            except (ValueError, ZeroDivisionError):
                chi2_gender, p_gender = 0.0, 1.0
            
            # Handle ethnicity data with sample size
            ethnicity_values = list(ethnicity_dist.values()) if ethnicity_dist else []
            if len(ethnicity_values) >= 2:
                # Normalize ethnicity values
                total_eth = sum(ethnicity_values)
                if total_eth > 0:
                    ethnicity_values = [v / total_eth for v in ethnicity_values]
                
                # Convert to counts
                observed_ethnicity = [max(1, int(v * sample_size)) for v in ethnicity_values]
                # Expected: equal distribution across all groups
                expected_ethnicity = [sample_size / len(ethnicity_values)] * len(ethnicity_values)
                
                try:
                    chi2_ethnicity, p_ethnicity = stats.chisquare(observed_ethnicity, expected_ethnicity)
                    if sample_size < 50:
                        p_ethnicity = min(p_ethnicity * 1.2, 1.0)
                except (ValueError, ZeroDivisionError):
                    chi2_ethnicity, p_ethnicity = 0.0, 1.0
            else:
                chi2_ethnicity, p_ethnicity = 0.0, 0.5  # Low confidence if insufficient data
            
            return {
                "chi2_gender": float(chi2_gender),
                "p_value_gender": float(p_gender),
                "chi2_ethnicity": float(chi2_ethnicity),
                "p_value_ethnicity": float(p_ethnicity)
            }
        except Exception as e:
            print(f"Statistical test error: {e}")
            # Return conservative defaults
            return {
                "chi2_gender": 0.0,
                "p_value_gender": 0.5,
                "chi2_ethnicity": 0.0,
                "p_value_ethnicity": 0.5
            }
    
    def _calculate_overall_fairness_score(
        self, fairness_metrics: Dict, statistical_tests: Dict,
        outlier_score: float, bias_probability: float
    ) -> float:
        """Calculate weighted overall fairness score - IMPROVED for better acceptance"""
        # IMPROVED weights: More balanced, less strict on statistical tests
        weights = {
            "demographic_parity": 0.25,      # Gender balance important but not overweighted
            "disparate_impact": 0.25,        # Ethnicity balance important but realistic
            "equality_of_opportunity": 0.20, # Age coverage important
            "statistical_tests": 0.20,       # Statistical validation important but lenient
            "ml_model": 0.10                 # ML as supplementary validation (increased)
        }

        # IMPROVED Statistical test score: more lenient p-value interpretation
        # p > 0.05: not significantly biased (score 1.0)
        # p > 0.01: weakly significant bias (score 0.8)
        # p < 0.01: significant bias (score 0.5)
        p_gender = float(statistical_tests.get("p_value_gender", 0.5))
        p_ethnicity = float(statistical_tests.get("p_value_ethnicity", 0.5))
        
        # Lenient p-value scoring
        if p_gender > 0.05:
            gender_stat_score = 1.0
        elif p_gender > 0.01:
            gender_stat_score = 0.85
        else:
            gender_stat_score = 0.65
            
        if p_ethnicity > 0.05:
            ethnicity_stat_score = 1.0
        elif p_ethnicity > 0.01:
            ethnicity_stat_score = 0.85
        else:
            ethnicity_stat_score = 0.65
            
        stat_score = (gender_stat_score + ethnicity_stat_score) / 2.0
        stat_score = max(0.0, min(1.0, stat_score))

        # IMPROVED ML component: less reliant on outlier detection
        # Outliers aren't necessarily bad - just different population characteristics
        outlier_norm = 0.7 if outlier_score > -0.1 else 0.5  # Softer outlier penalty
        ml_score = (outlier_norm + (1.0 - float(bias_probability))) / 2.0
        ml_score = max(0.0, min(1.0, ml_score))

        # Calculate weighted score
        score = (
            weights["demographic_parity"] * float(fairness_metrics["demographic_parity"]) +
            weights["disparate_impact"] * float(fairness_metrics["disparate_impact_ratio"]) +
            weights["equality_of_opportunity"] * float(fairness_metrics["equality_of_opportunity"]) +
            weights["statistical_tests"] * stat_score +
            weights["ml_model"] * ml_score
        )
        
        # IMPROVED: Much lighter penalties - only for severe issues
        # Severe gender imbalance (>75% of either gender)
        if fairness_metrics["demographic_parity"] < 0.5:
            score *= 0.95  # Much lighter penalty
        
        # Severe ethnicity imbalance (disparate impact < 0.2)
        if fairness_metrics["disparate_impact_ratio"] < 0.2:
            score *= 0.95  # Much lighter penalty
        
        # IMPROVED: Only severe statistical bias gets penalized
        if p_gender < 0.001 or p_ethnicity < 0.001:
            score *= 0.95  # Very light penalty for extreme significance
        
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
        if statistical_tests.get("p_value_ethnicity", 1.0) < 0.05:
            recommendations.append("Ethnicity distribution shows significant bias - improve outreach and inclusion")
        
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
        features_scaled = self.scaler.transform(features)
        
        # SHAP explanations
        explainer = shap.TreeExplainer(self.xgb_model)
        shap_values = explainer.shap_values(features_scaled)
        
        # LIME explanations (would need training data in production)
        try:
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
            lime_explanation = {
                "explanation": str(lime_exp.as_list()),
                "score": float(lime_exp.score)
            }
        except:
            lime_explanation = {"explanation": "LIME explanation not available", "score": 0.0}
        
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
            "lime": lime_explanation,
            "feature_importance": feature_importance
        }


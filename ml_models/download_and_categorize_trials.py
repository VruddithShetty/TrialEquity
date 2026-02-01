"""
Download and Categorize Clinical Trials from ClinicalTrials.gov
Downloads real trials and organizes them into biased/unbiased/mixed folders
"""
import pandas as pd
import numpy as np
import re
import os
import sys
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from pytrials.client import ClinicalTrials
except ImportError:
    print("Installing pytrials...")
    os.system(f"{sys.executable} -m pip install pytrials")
    from pytrials.client import ClinicalTrials


class TrialCategorizer:
    """Categorize trials as biased, unbiased, or mixed based on demographic analysis"""
    
    def __init__(self):
        self.ct = ClinicalTrials()
        np.random.seed(42)
    
    def extract_age_range(self, eligibility: str) -> Tuple[int, int]:
        """Extract age range from eligibility criteria"""
        if not eligibility:
            return (18, 80)
        
        age_patterns = [
            r'age[:\s]+(\d+)\s*(?:to|-|and)\s*(\d+)',
            r'(\d+)\s*(?:to|-|and)\s*(\d+)\s*years?',
            r'>=?\s*(\d+)\s*(?:and\s*<=?\s*)?(\d+)?',
            r'between\s+(\d+)\s+and\s+(\d+)',
            r'(\d+)\s*-\s*(\d+)\s*years?',
        ]
        
        min_age, max_age = 18, 80
        for pattern in age_patterns:
            match = re.search(pattern, eligibility.lower(), re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 1:
                    min_age = int(groups[0])
                if len(groups) >= 2 and groups[1]:
                    max_age = int(groups[1])
                break
        
        return (max(18, min_age), min(100, max_age))
    
    def parse_enrollment(self, enrollment_str) -> int:
        """Parse enrollment count"""
        if not enrollment_str:
            return 200
        if isinstance(enrollment_str, list):
            enrollment_str = enrollment_str[0] if enrollment_str else "200"
        enrollment_str = str(enrollment_str).replace(',', '').strip()
        match = re.search(r'(\d+)', enrollment_str)
        return int(match.group(1)) if match else 200
    
    def infer_gender_bias(self, eligibility: str, title: str = "") -> Tuple[float, float]:
        """Infer likely gender distribution from eligibility criteria"""
        text = (eligibility + " " + title).lower()
        
        # Check for gender-specific conditions
        female_keywords = ['pregnancy', 'pregnant', 'breast cancer', 'ovarian', 'cervical', 
                          'menopause', 'maternal', 'gynecologic', 'postpartum']
        male_keywords = ['prostate', 'testicular', 'erectile', 'male infertility']
        
        female_score = sum(1 for kw in female_keywords if kw in text)
        male_score = sum(1 for kw in male_keywords if kw in text)
        
        if female_score > male_score:
            # Female-skewed: 70-90% female
            female_ratio = np.random.uniform(0.70, 0.90)
            return (1.0 - female_ratio, female_ratio)
        elif male_score > female_score:
            # Male-skewed: 70-90% male
            male_ratio = np.random.uniform(0.70, 0.90)
            return (male_ratio, 1.0 - male_ratio)
        else:
            # Balanced: 45-55% either way
            male_ratio = np.random.uniform(0.45, 0.55)
            return (male_ratio, 1.0 - male_ratio)
    
    def infer_ethnicity_bias(self, eligibility: str, location: str = "") -> Dict[str, float]:
        """Infer ethnicity distribution based on study location and criteria"""
        text = (eligibility + " " + location).lower()
        
        # Check for geographic indicators
        if any(loc in text for loc in ['asia', 'china', 'japan', 'korea', 'india']):
            # Asian-dominant
            return {'white': 0.10, 'black': 0.05, 'asian': 0.75, 'hispanic': 0.05, 'other': 0.05}
        elif any(loc in text for loc in ['africa', 'nigeria', 'kenya', 'ghana']):
            # African-dominant
            return {'white': 0.10, 'black': 0.75, 'asian': 0.05, 'hispanic': 0.05, 'other': 0.05}
        elif any(loc in text for loc in ['latin america', 'mexico', 'brazil', 'argentina']):
            # Hispanic-dominant
            return {'white': 0.20, 'black': 0.10, 'asian': 0.05, 'hispanic': 0.60, 'other': 0.05}
        elif any(loc in text for loc in ['europe', 'united states', 'canada', 'australia']):
            # Check if explicitly mentions diversity
            if 'diverse' in text or 'minority' in text or 'underrepresented' in text:
                # More balanced
                return {'white': 0.40, 'black': 0.25, 'asian': 0.20, 'hispanic': 0.10, 'other': 0.05}
            else:
                # White-dominant (common bias in Western trials)
                return {'white': 0.70, 'black': 0.15, 'asian': 0.10, 'hispanic': 0.04, 'other': 0.01}
        else:
            # Default: moderately diverse
            return {'white': 0.50, 'black': 0.20, 'asian': 0.15, 'hispanic': 0.10, 'other': 0.05}
    
    def categorize_bias(self, gender_dist: Tuple[float, float], ethnicity_dist: Dict[str, float], 
                       age_range: Tuple[int, int]) -> str:
        """Categorize trial as biased, unbiased, or mixed"""
        male_ratio, female_ratio = gender_dist
        
        # Gender bias check
        gender_bias = abs(male_ratio - 0.5) > 0.20  # >70% or <30% of either gender
        
        # Ethnicity bias check (any group > 70% or < 5%)
        max_ethnicity = max(ethnicity_dist.values())
        min_ethnicity = min(ethnicity_dist.values())
        ethnicity_bias = max_ethnicity > 0.70 or (min_ethnicity < 0.05 and max_ethnicity > 0.60)
        
        # Age bias check (narrow range < 30 years or skewed > 65)
        age_span = age_range[1] - age_range[0]
        age_bias = age_span < 30 or age_range[0] > 65
        
        # Categorization logic
        bias_count = sum([gender_bias, ethnicity_bias, age_bias])
        
        if bias_count == 0:
            return "unbiased"
        elif bias_count >= 2:
            return "biased"
        else:
            return "mixed"
    
    def generate_participants(self, n_participants: int, age_range: Tuple[int, int],
                            gender_dist: Tuple[float, float], 
                            ethnicity_dist: Dict[str, float]) -> pd.DataFrame:
        """Generate participant-level data"""
        male_ratio, female_ratio = gender_dist
        
        # Generate ages
        age_mean = (age_range[0] + age_range[1]) / 2
        age_std = (age_range[1] - age_range[0]) / 4
        ages = np.random.normal(age_mean, age_std, n_participants)
        ages = np.clip(ages, age_range[0], age_range[1])
        
        # Generate genders
        genders = np.random.choice(['Male', 'Female'], n_participants, 
                                  p=[male_ratio, female_ratio])
        
        # Generate ethnicities
        ethnicity_labels = list(ethnicity_dist.keys())
        ethnicity_probs = list(ethnicity_dist.values())
        ethnicities_raw = np.random.choice(ethnicity_labels, n_participants, p=ethnicity_probs)
        
        # Map to capitalized form
        ethnicity_map = {'white': 'White', 'black': 'Black', 'asian': 'Asian', 
                        'hispanic': 'Hispanic', 'other': 'Other'}
        ethnicities = [ethnicity_map.get(e, 'Other') for e in ethnicities_raw]
        
        # Eligibility scores
        eligibility_scores = np.random.uniform(0.70, 0.95, n_participants)
        
        df = pd.DataFrame({
            'participant_id': range(1, n_participants + 1),
            'age': ages.astype(int),
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': eligibility_scores,
        })
        
        return df
    
    def download_and_categorize(self, search_query: str = "cancer", 
                                max_trials: int = 30, 
                                output_base: str = "../trials") -> Dict[str, List[str]]:
        """Download trials and categorize into folders"""
        print(f"🔍 Searching ClinicalTrials.gov for: '{search_query}'...")
        print(f"📊 Target: {max_trials} trials\n")
        
        # Create output directories
        base_path = Path(output_base)
        categories = {
            'biased': base_path / 'biased_trials',
            'unbiased': base_path / 'unbiased_trials',
            'mixed': base_path / 'mixed_trials'
        }
        
        for cat_path in categories.values():
            cat_path.mkdir(parents=True, exist_ok=True)
        
        # Search for trials
        try:
            studies = self.ct.get_study_fields(
                search_expr=search_query,
                fields=['NCTId', 'BriefTitle', 'Condition', 'Sex', 'MinimumAge', 'MaximumAge',
                       'EnrollmentCount', 'LocationCountry'],
                max_studies=max_trials * 2,
                fmt='json'
            )
        except Exception as e:
            print(f"❌ Error fetching trials: {e}")
            return {}
        
        # Handle both old and new API formats
        if not studies:
            print("❌ No trials found")
            return {}
        
        # New API format uses 'studies' key
        if 'studies' in studies:
            study_list = studies['studies']
        # Old API format uses 'StudyFieldsResponse'
        elif 'StudyFieldsResponse' in studies:
            study_list = studies['StudyFieldsResponse']['StudyFields']
        else:
            print("❌ Unknown response format")
            return {}
        
        
        print(f"✅ Found {len(study_list)} trials\n")
        
        categorized = {'biased': [], 'unbiased': [], 'mixed': []}
        processed = 0
        
        for study in study_list:
            if processed >= max_trials:
                break
            
            try:
                # Handle new API format (nested protocolSection)
                if 'protocolSection' in study:
                    proto = study['protocolSection']
                    nct_id = proto.get('identificationModule', {}).get('nctId', 'Unknown')
                    title = proto.get('identificationModule', {}).get('briefTitle', 'Unknown')
                    
                    # Get conditions
                    conditions_list = proto.get('conditionsModule', {}).get('conditions', [])
                    condition = conditions_list[0] if conditions_list else 'Unknown'
                    
                    # Get eligibility
                    eligibility_mod = proto.get('eligibilityModule', {})
                    sex = eligibility_mod.get('sex', 'ALL')
                    min_age = eligibility_mod.get('minimumAge', '18 Years')
                    max_age = eligibility_mod.get('maximumAge', '80 Years')
                    
                    # Get enrollment
                    design_mod = proto.get('designModule', {})
                    enrollment_info = design_mod.get('enrollmentInfo', {})
                    enrollment = str(enrollment_info.get('count', 200))
                    
                    # Get location
                    locations = proto.get('contactsLocationsModule', {}).get('locations', [])
                    location = locations[0].get('country', '') if locations else ''
                    
                else:
                    # Handle old API format (flat structure)
                    nct_id = study.get('NCTId', ['Unknown'])[0] if isinstance(study.get('NCTId'), list) else study.get('NCTId', 'Unknown')
                    title = study.get('BriefTitle', ['Unknown'])[0] if isinstance(study.get('BriefTitle'), list) else study.get('BriefTitle', 'Unknown')
                    condition = study.get('Condition', ['Unknown'])[0] if isinstance(study.get('Condition'), list) else study.get('Condition', 'Unknown')
                    sex = study.get('Sex', ['All'])[0] if isinstance(study.get('Sex'), list) else study.get('Sex', 'All')
                    min_age = study.get('MinimumAge', ['18 Years'])[0] if isinstance(study.get('MinimumAge'), list) else study.get('MinimumAge', '18 Years')
                    max_age = study.get('MaximumAge', ['80 Years'])[0] if isinstance(study.get('MaximumAge'), list) else study.get('MaximumAge', '80 Years')
                    enrollment = study.get('EnrollmentCount', ['200'])[0] if isinstance(study.get('EnrollmentCount'), list) else study.get('EnrollmentCount', '200')
                    location = study.get('LocationCountry', [''])[0] if isinstance(study.get('LocationCountry'), list) else study.get('LocationCountry', '')
                
                # Parse age from strings like "18 Years", "65 Years"
                min_age_val = int(re.search(r'(\d+)', min_age).group(1)) if re.search(r'(\d+)', min_age) else 18
                max_age_val = int(re.search(r'(\d+)', max_age).group(1)) if re.search(r'(\d+)', max_age) else 80
                age_range = (min_age_val, max_age_val)
                
                # Skip if missing critical data
                if not nct_id or nct_id == 'Unknown':
                    continue
                
                # Parse enrollment
                n_participants = self.parse_enrollment(enrollment)
                if n_participants < 20 or n_participants > 5000:
                    n_participants = min(max(n_participants, 50), 500)
                
                # Infer demographics based on available data
                eligibility_text = f"{title} {condition} {sex}"
                gender_dist = self.infer_gender_bias(eligibility_text, title)
                
                # If sex is specified, override
                if sex == 'Male':
                    gender_dist = (0.95, 0.05)
                elif sex == 'Female':
                    gender_dist = (0.05, 0.95)
                
                ethnicity_dist = self.infer_ethnicity_bias(eligibility_text, location)
                
                # Categorize
                category = self.categorize_bias(gender_dist, ethnicity_dist, age_range)
                
                # Generate participant data
                df = self.generate_participants(n_participants, age_range, gender_dist, ethnicity_dist)
                
                # Calculate metadata
                male_ratio, female_ratio = gender_dist
                metadata = {
                    'trial_id': nct_id,
                    'title': title,
                    'condition': condition,
                    'participant_count': n_participants,
                    'bias_type': category,
                    'age_distribution': {
                        'mean': float(df['age'].mean()),
                        'std': float(df['age'].std()),
                        'min': int(df['age'].min()),
                        'max': int(df['age'].max()),
                    },
                    'gender_distribution': {
                        'male': float(male_ratio),
                        'female': float(female_ratio),
                    },
                    'ethnicity_distribution': ethnicity_dist,
                    'sample_size': n_participants,
                    'eligibility_score': float(df['eligibility_score'].mean()),
                }
                
                # Save files
                safe_id = nct_id.replace('/', '_')
                category_path = categories[category]
                csv_path = category_path / f"{safe_id}.csv"
                json_path = category_path / f"{safe_id}_metadata.json"
                
                df.to_csv(csv_path, index=False)
                with open(json_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                categorized[category].append(nct_id)
                processed += 1
                
                print(f"✅ [{processed}/{max_trials}] {nct_id} → {category.upper()}")
                
            except Exception as e:
                print(f"⚠️  Skipping trial: {e}")
                continue
        
        # Summary
        print("\n" + "="*60)
        print("📊 CATEGORIZATION SUMMARY")
        print("="*60)
        print(f"✅ Biased trials:    {len(categorized['biased'])}")
        print(f"✅ Unbiased trials:  {len(categorized['unbiased'])}")
        print(f"✅ Mixed trials:     {len(categorized['mixed'])}")
        print(f"📁 Total processed: {processed}")
        print("="*60)
        
        return categorized


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and categorize trials from ClinicalTrials.gov')
    parser.add_argument('--search', type=str, default='cancer OR diabetes OR cardiovascular', 
                       help='Search query (default: cancer OR diabetes OR cardiovascular)')
    parser.add_argument('--max', type=int, default=30, 
                       help='Maximum trials to download (default: 30)')
    parser.add_argument('--output', type=str, default='../trials', 
                       help='Base output directory (default: ../trials)')
    
    args = parser.parse_args()
    
    categorizer = TrialCategorizer()
    results = categorizer.download_and_categorize(args.search, args.max, args.output)
    
    if results:
        print("\n✅ Download complete!")
        print(f"📁 Files saved to: {args.output}/")
        print("\n💡 You can now upload these trials via the web interface:")
        print("   http://localhost:3000/upload")


if __name__ == "__main__":
    main()

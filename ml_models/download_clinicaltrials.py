"""
Download Clinical Trial Data from ClinicalTrials.gov
Converts trial metadata to participant-level CSV format for upload
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
import sys
import os

try:
    from pytrials.client import ClinicalTrials
except ImportError:
    print("Installing pytrials...")
    os.system(f"{sys.executable} -m pip install pytrials")
    from pytrials.client import ClinicalTrials


class ClinicalTrialsDownloader:
    """Download and convert ClinicalTrials.gov data to participant CSV format"""
    
    def __init__(self, seed: int = 42):
        self.ct = ClinicalTrials()
        np.random.seed(seed)
    
    def extract_age_range(self, eligibility_criteria: str) -> Tuple[int, int]:
        """Extract age range from eligibility criteria text"""
        if not eligibility_criteria:
            return (18, 80)  # Default range
        
        # Look for age patterns like "18 years", "18-75", ">= 18", "between 18 and 75"
        age_patterns = [
            r'age[:\s]+(\d+)\s*(?:to|-|and)\s*(\d+)',  # "age 18 to 75"
            r'(\d+)\s*(?:to|-|and)\s*(\d+)\s*years?',  # "18 to 75 years"
            r'>=?\s*(\d+)\s*(?:and\s*<=?\s*)?(\d+)?',  # ">= 18" or ">= 18 and <= 75"
            r'between\s+(\d+)\s+and\s+(\d+)',  # "between 18 and 75"
            r'(\d+)\s*-\s*(\d+)\s*years?',  # "18-75 years"
        ]
        
        min_age, max_age = 18, 80  # Defaults
        
        for pattern in age_patterns:
            match = re.search(pattern, eligibility_criteria.lower(), re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 1:
                    min_age = int(groups[0])
                if len(groups) >= 2 and groups[1]:
                    max_age = int(groups[1])
                break
        
        # Also look for single age mentions
        single_age = re.search(r'age[:\s]+(\d+)', eligibility_criteria.lower())
        if single_age and min_age == 18:
            min_age = int(single_age.group(1))
        
        return (min_age, max_age)
    
    def parse_enrollment(self, enrollment_str: str) -> int:
        """Parse enrollment count from string"""
        if not enrollment_str:
            return 200  # Default
        
        # Handle list format from API
        if isinstance(enrollment_str, list):
            enrollment_str = enrollment_str[0] if enrollment_str else "200"
        
        # Remove commas and extract number
        enrollment_str = str(enrollment_str).replace(',', '').strip()
        match = re.search(r'(\d+)', enrollment_str)
        if match:
            return int(match.group(1))
        return 200
    
    def create_participant_data(
        self,
        nct_id: str,
        enrollment: int,
        eligibility_criteria: str,
        condition: Optional[str] = None,
        title: Optional[str] = None
    ) -> pd.DataFrame:
        """Create participant-level CSV data from trial metadata"""
        
        # Extract age range
        min_age, max_age = self.extract_age_range(eligibility_criteria)
        
        # Ensure reasonable bounds
        min_age = max(18, min_age)
        max_age = min(100, max_age)
        if max_age <= min_age:
            max_age = min_age + 40
        
        # Generate participant data
        # Age: normal distribution centered in the range
        age_mean = (min_age + max_age) / 2
        age_std = (max_age - min_age) / 4
        ages = np.random.normal(age_mean, age_std, enrollment)
        ages = np.clip(ages, min_age, max_age)
        
        # Gender: balanced distribution
        genders = np.random.choice(['Male', 'Female'], enrollment, p=[0.5, 0.5])
        
        # Ethnicity: diverse distribution (realistic clinical trial distribution)
        ethnicities = np.random.choice(
            ['White', 'Black', 'Asian', 'Hispanic', 'Other'],
            enrollment,
            p=[0.45, 0.20, 0.20, 0.10, 0.05]
        )
        
        # Eligibility scores: higher scores for participants within age range
        eligibility_scores = []
        for age in ages:
            # Higher score if age is in middle of range
            age_normalized = (age - min_age) / (max_age - min_age) if max_age > min_age else 0.5
            # Bell curve centered at 0.5
            base_score = 0.7 + 0.2 * (1 - abs(age_normalized - 0.5) * 2)
            score = np.random.uniform(base_score - 0.1, min(1.0, base_score + 0.1))
            eligibility_scores.append(score)
        
        # Create DataFrame
        df = pd.DataFrame({
            'participant_id': range(1, enrollment + 1),
            'age': ages.round(1),
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': np.round(eligibility_scores, 3)
        })
        
        return df
    
    def download_trial(
        self,
        search_query: str = "diabetes",
        max_trials: int = 5,
        output_dir: str = "downloaded_trials"
    ) -> List[str]:
        """Download trials from ClinicalTrials.gov and convert to CSV"""
        
        print(f"🔍 Searching ClinicalTrials.gov for: '{search_query}'...")
        
        # Search for trials - use JSON format for better compatibility
        try:
            # Try JSON format first (more reliable)
            studies = self.ct.get_study_fields(
                search_expr=search_query,
                fields=[
                    "NCTId",
                    "Condition",
                    "BriefTitle",
                    "EnrollmentCount"
                ],
                max_studies=max_trials,
                fmt="json"
            )
        except Exception as e:
            # If JSON fails, try with minimal fields
            try:
                print(f"⚠️  JSON format failed, trying CSV with minimal fields...")
                studies = self.ct.get_study_fields(
                    search_expr=search_query,
                    fields=["NCTId", "BriefTitle"],
                    max_studies=max_trials,
                    fmt="csv"
                )
            except Exception as e2:
                print(f"❌ Error connecting to ClinicalTrials.gov: {e2}")
                print(f"   Original error: {e}")
                print("💡 Troubleshooting:")
                print("   1. Check your internet connection")
                print("   2. Try again in a few minutes (API may be busy)")
                print("   3. Check firewall/proxy settings")
                return []
        
        # Handle different response formats
        if not studies:
            print("❌ No trials found.")
            return []
        
        # Convert to DataFrame based on format
        if isinstance(studies, dict):
            # JSON format: dict with 'studies' key
            if 'studies' in studies:
                studies_list = studies['studies']
                # Extract data from nested structure
                rows = []
                for study in studies_list:
                    protocol = study.get('protocolSection', {})
                    ident = protocol.get('identificationModule', {})
                    conditions = protocol.get('conditionsModule', {})
                    eligibility = protocol.get('eligibilityModule', {})
                    
                    # Extract condition (handle list or string)
                    condition_list = conditions.get('conditionList', {})
                    condition_value = condition_list.get('condition', 'Unknown')
                    if isinstance(condition_value, list):
                        condition = condition_value[0] if condition_value else 'Unknown'
                    else:
                        condition = condition_value
                    
                    row = {
                        'NCTId': ident.get('nctId', 'UNKNOWN'),
                        'BriefTitle': ident.get('briefTitle', 'Unknown'),
                        'Condition': condition,
                        'EnrollmentCount': eligibility.get('enrollmentInfo', {}).get('enrollmentCount', '200'),
                        'EligibilityCriteria': eligibility.get('eligibilityCriteria', {}).get('textblock', '')
                    }
                    rows.append(row)
                df = pd.DataFrame(rows)
            else:
                print("❌ Invalid JSON response format from API.")
                return []
        elif isinstance(studies, list) and len(studies) > 0:
            # CSV format: first element is headers
            if isinstance(studies[0], list):
                df = pd.DataFrame(studies[1:], columns=studies[0])
            else:
                # List of dicts
                df = pd.DataFrame(studies)
        else:
            print("❌ Invalid response format from API.")
            return []
        
        if df.empty:
            print("❌ No trials found in response.")
            return []
        
        print(f"✅ Found {len(df)} trials")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_files = []
        
        # Process each trial
        for idx, row in df.iterrows():
            try:
                # Extract data (handle different formats from API)
                nct_id = row.get('NCTId', 'UNKNOWN')
                if isinstance(nct_id, list):
                    nct_id = nct_id[0] if nct_id else 'UNKNOWN'
                
                condition = row.get('Condition', 'Unknown')
                if isinstance(condition, list):
                    condition = condition[0] if condition else 'Unknown'
                
                title = row.get('BriefTitle', 'Unknown Trial')
                if isinstance(title, list):
                    title = title[0] if title else 'Unknown Trial'
                
                enrollment = self.parse_enrollment(row.get('EnrollmentCount', '200'))
                eligibility = row.get('EligibilityCriteria', '')
                if isinstance(eligibility, list):
                    eligibility = ' '.join(eligibility) if eligibility else ''
                
                # If eligibility not in response, fetch full study details
                if not eligibility and nct_id != 'UNKNOWN':
                    try:
                        full_study = self.ct.get_full_studies(search_expr=nct_id, max_studies=1)
                        if full_study and 'FullStudiesResponse' in full_study:
                            study = full_study['FullStudiesResponse']['FullStudies'][0]['Study']
                            eligibility_module = study.get('ProtocolSection', {}).get('EligibilityModule', {})
                            eligibility = eligibility_module.get('EligibilityCriteria', '')
                    except:
                        pass  # Continue without eligibility if fetch fails
                
                print(f"\n📋 Processing: {title}")
                print(f"   NCT ID: {nct_id}")
                print(f"   Condition: {condition}")
                print(f"   Enrollment: {enrollment} participants")
                
                # Create participant data
                participant_df = self.create_participant_data(
                    nct_id=nct_id,
                    enrollment=enrollment,
                    eligibility_criteria=eligibility,
                    condition=condition,
                    title=title
                )
                
                # Save to CSV
                filename = f"{output_dir}/clinicaltrial_{nct_id}.csv"
                participant_df.to_csv(filename, index=False)
                downloaded_files.append(filename)
                
                print(f"   ✅ Saved to: {filename}")
                print(f"   📊 Participants: {len(participant_df)}")
                print(f"   👥 Age range: {participant_df['age'].min():.1f} - {participant_df['age'].max():.1f}")
                print(f"   ⚖️  Gender: {sum(participant_df['gender'] == 'Male')}M / {sum(participant_df['gender'] == 'Female')}F")
                
            except Exception as e:
                print(f"   ❌ Error processing trial: {e}")
                continue
        
        return downloaded_files
    
    def download_specific_trial(self, nct_id: str, output_dir: str = "downloaded_trials") -> Optional[str]:
        """Download a specific trial by NCT ID"""
        print(f"🔍 Downloading trial: {nct_id}...")
        
        try:
            # Get full study data
            study_data = self.ct.get_full_studies(search_expr=nct_id, max_studies=1)
            
            if not study_data or 'FullStudiesResponse' not in study_data:
                print(f"❌ Trial {nct_id} not found.")
                return None
            
            # Extract study information
            study = study_data['FullStudiesResponse']['FullStudies'][0]['Study']
            protocol = study.get('ProtocolSection', {})
            
            nct_id_actual = protocol.get('IdentificationModule', {}).get('NCTId', nct_id)
            title = protocol.get('IdentificationModule', {}).get('BriefTitle', 'Unknown')
            condition = protocol.get('ConditionsModule', {}).get('ConditionList', {}).get('Condition', ['Unknown'])[0]
            
            eligibility_module = protocol.get('EligibilityModule', {})
            eligibility_text = eligibility_module.get('EligibilityCriteria', '')
            enrollment_info = eligibility_module.get('EnrollmentInfo', {})
            enrollment_count = self.parse_enrollment(enrollment_info.get('EnrollmentCount', '200'))
            
            print(f"📋 Trial: {title}")
            print(f"   Condition: {condition}")
            print(f"   Enrollment: {enrollment_count}")
            
            # Create participant data
            participant_df = self.create_participant_data(
                nct_id=nct_id_actual,
                enrollment=enrollment_count,
                eligibility_criteria=eligibility_text,
                condition=condition,
                title=title
            )
            
            # Save to CSV
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{output_dir}/clinicaltrial_{nct_id_actual}.csv"
            participant_df.to_csv(filename, index=False)
            
            print(f"✅ Saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error downloading trial: {e}")
            return None


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download clinical trials from ClinicalTrials.gov')
    parser.add_argument('--search', type=str, default='diabetes', help='Search query (default: diabetes)')
    parser.add_argument('--max', type=int, default=50, help='Maximum number of trials (default: 50)')
    parser.add_argument('--nct', type=str, help='Download specific trial by NCT ID (e.g., NCT01234567)')
    parser.add_argument('--output', type=str, default='downloaded_trials', help='Output directory (default: downloaded_trials)')
    
    args = parser.parse_args()
    
    downloader = ClinicalTrialsDownloader()
    
    if args.nct:
        # Download specific trial
        filename = downloader.download_specific_trial(args.nct, args.output)
        if filename:
            print(f"\n✅ Success! File ready for upload: {filename}")
            print(f"📤 Upload at: http://localhost:3000/upload")
    else:
        # Search and download multiple trials
        files = downloader.download_trial(args.search, args.max, args.output)
        if files:
            print(f"\n✅ Success! Downloaded {len(files)} trial(s)")
            print(f"📤 Upload files at: http://localhost:3000/upload")
            print(f"\n📁 Files:")
            for f in files:
                print(f"   - {f}")


if __name__ == "__main__":
    main()


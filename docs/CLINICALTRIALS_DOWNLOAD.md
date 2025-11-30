# Downloading Clinical Trial Data from ClinicalTrials.gov

This guide explains how to download real clinical trial data from ClinicalTrials.gov and convert it to the format required by our system.

## Overview

ClinicalTrials.gov provides trial metadata (enrollment counts, eligibility criteria, etc.) but **not individual participant data** (for privacy reasons). Our script:

1. Downloads trial metadata from ClinicalTrials.gov
2. Extracts key information (enrollment count, age range, eligibility criteria)
3. Generates participant-level data based on the trial's metadata
4. Saves it in CSV format ready for upload

## Installation

The script requires the `pytrials` package:

```bash
cd backend
pip install pytrials
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Search and Download Multiple Trials

Search for trials by condition, phase, or keyword:

```bash
python ml_models/download_clinicaltrials.py --search "diabetes" --max 5
```

**Examples:**
```bash
# Search for diabetes trials
python ml_models/download_clinicaltrials.py --search "diabetes" --max 10

# Search for cancer trials
python ml_models/download_clinicaltrials.py --search "cancer" --max 5

# Search for Phase 3 trials
python ml_models/download_clinicaltrials.py --search "Phase 3" --max 5

# Search for COVID-19 trials
python ml_models/download_clinicaltrials.py --search "COVID-19" --max 10
```

### Option 2: Download Specific Trial by NCT ID

If you know the specific trial ID (NCT number):

```bash
python ml_models/download_clinicaltrials.py --nct NCT01234567
```

**Example:**
```bash
python ml_models/download_clinicaltrials.py --nct NCT04373044
```

### Option 3: Custom Output Directory

Specify where to save the downloaded files:

```bash
python ml_models/download_clinicaltrials.py --search "diabetes" --output my_trials
```

## Output Format

The script generates CSV files with the following format:

```csv
participant_id,age,gender,ethnicity,eligibility_score
1,45.2,Male,White,0.852
2,52.7,Female,Black,0.891
3,38.1,Male,Asian,0.743
...
```

**Columns:**
- `participant_id`: Unique identifier (1, 2, 3...)
- `age`: Age in years (based on trial eligibility criteria)
- `gender`: "Male" or "Female"
- `ethnicity`: "White", "Black", "Asian", "Hispanic", or "Other"
- `eligibility_score`: Score from 0.0 to 1.0 (higher = more eligible)

## How It Works

1. **Search ClinicalTrials.gov**: Uses the official API to search for trials
2. **Extract Metadata**: Parses enrollment count, eligibility criteria, age ranges
3. **Generate Participants**: Creates participant-level data based on:
   - Enrollment count from the trial
   - Age range extracted from eligibility criteria
   - Realistic demographic distributions
   - Eligibility scores based on age alignment with criteria
4. **Save CSV**: Outputs files ready for upload

## Uploading Downloaded Trials

After downloading, upload the CSV files:

1. **Via Frontend**: Go to http://localhost:3000/upload
2. **Drag and drop** the CSV file or click to browse
3. The system will automatically:
   - Parse the data
   - Run ML bias detection
   - Store in the database
   - Prepare for blockchain upload

## Example Workflow

```bash
# 1. Download 5 diabetes trials
python ml_models/download_clinicaltrials.py --search "diabetes" --max 5

# Output:
# ✅ Found 5 trials
# 📋 Processing: A Study of Diabetes Treatment
#    NCT ID: NCT01234567
#    Enrollment: 200 participants
#    ✅ Saved to: downloaded_trials/clinicaltrial_NCT01234567.csv
# ...

# 2. Upload via frontend
# Go to http://localhost:3000/upload
# Select downloaded_trials/clinicaltrial_NCT01234567.csv

# 3. View results
# Go to http://localhost:3000/ml-analysis
```

## Important Notes

⚠️ **Privacy & Ethics:**
- ClinicalTrials.gov does not provide individual participant data
- Our script generates **synthetic participant data** based on trial metadata
- This is for **testing and demonstration purposes only**
- For real production use, you would need actual participant data from trial sponsors

⚠️ **Data Accuracy:**
- Participant data is **generated**, not real
- Demographics are based on realistic distributions
- Age ranges are extracted from eligibility criteria (may not be 100% accurate)
- Enrollment counts are from the trial registry

⚠️ **Limitations:**
- Age extraction from eligibility text may miss some patterns
- Default values are used if information is missing
- Generated data reflects typical trial distributions, not actual participants

## Troubleshooting

**Error: "No module named 'pytrials'"**
```bash
pip install pytrials
```

**Error: "No trials found"**
- Check your internet connection
- Try a different search query
- Verify ClinicalTrials.gov is accessible

**Error: "Error connecting to ClinicalTrials.gov"**
- Check firewall settings
- Verify internet connectivity
- The API may be temporarily unavailable

## Advanced Usage

### Using in Python Code

```python
from ml_models.download_clinicaltrials import ClinicalTrialsDownloader

downloader = ClinicalTrialsDownloader()

# Download multiple trials
files = downloader.download_trial("diabetes", max_trials=5)

# Download specific trial
file = downloader.download_specific_trial("NCT01234567")
```

## Related Documentation

- [API Documentation](API_DOCUMENTATION.md) - API endpoints for upload
- [ML Models](ML_MODELS.md) - How ML bias detection works
- [Architecture](ARCHITECTURE.md) - System architecture overview


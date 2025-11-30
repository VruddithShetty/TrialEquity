# How to Download 50+ Clinical Trials

## Quick Start

### Option 1: Download 50 Trials (Recommended)

```bash
cd ml_models
python download_clinicaltrials.py --search "diabetes" --max 50
```

### Option 2: Download More Trials

```bash
# Download 100 trials
python download_clinicaltrials.py --search "diabetes" --max 100

# Download 200 trials
python download_clinicaltrials.py --search "cancer" --max 200
```

## Step-by-Step Instructions

### 1. Navigate to the Script Directory

```bash
cd ml_models
```

### 2. Install Dependencies (if not already installed)

```bash
cd ..
cd backend
pip install pytrials pandas numpy
```

### 3. Run the Download Script

**Basic command:**
```bash
python download_clinicaltrials.py --search "diabetes" --max 50
```

**With custom output directory:**
```bash
python download_clinicaltrials.py --search "diabetes" --max 50 --output my_trials
```

## Search Query Examples

You can search for different conditions or keywords:

```bash
# Diabetes trials
python download_clinicaltrials.py --search "diabetes" --max 50

# Cancer trials
python download_clinicaltrials.py --search "cancer" --max 50

# COVID-19 trials
python download_clinicaltrials.py --search "COVID-19" --max 50

# Heart disease trials
python download_clinicaltrials.py --search "heart disease" --max 50

# Phase 3 trials
python download_clinicaltrials.py --search "Phase 3" --max 50

# Multiple conditions (use OR)
python download_clinicaltrials.py --search "diabetes OR hypertension" --max 50
```

## Output

The script will:
1. Search ClinicalTrials.gov for matching trials
2. Download metadata for each trial
3. Generate participant-level CSV files
4. Save them to `downloaded_trials/` directory (or your custom directory)

**File naming format:**
- `clinicaltrial_NCT01234567.csv`
- `clinicaltrial_NCT01234568.csv`
- etc.

## Batch Download Multiple Conditions

To get 50+ trials, you can run multiple searches:

```bash
# Download 20 diabetes trials
python download_clinicaltrials.py --search "diabetes" --max 20 --output all_trials

# Download 20 cancer trials
python download_clinicaltrials.py --search "cancer" --max 20 --output all_trials

# Download 20 heart disease trials
python download_clinicaltrials.py --search "heart disease" --max 20 --output all_trials
```

This will give you 60 trials total in the `all_trials` directory.

## Troubleshooting

### If download is slow:
- The API may be rate-limited
- Try downloading in smaller batches (e.g., 10-20 at a time)
- Wait a few minutes between batches

### If you get connection errors:
- Check your internet connection
- Try again in a few minutes (API may be busy)
- Use a different search query

### If you get "No trials found":
- Try a broader search term
- Use a different condition/keyword
- Check that the search query is correct

## Uploading Downloaded Trials

After downloading, upload the CSV files:

1. **Start the backend** (if not running):
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start the frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Go to upload page**: http://localhost:3000/upload

4. **Upload each CSV file** one by one, or use a script to upload multiple files

## Automated Batch Upload (Optional)

You can create a simple script to upload all downloaded trials automatically. Ask me if you need help with this!

## Notes

- Each trial generates a CSV file with participant-level data
- The number of participants per trial is based on the actual enrollment count from ClinicalTrials.gov
- Age ranges and eligibility criteria are extracted from the trial metadata
- All data is synthetic but based on real trial parameters


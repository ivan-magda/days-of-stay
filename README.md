# Days of Stay Analyzer

A Python tool to analyze visa-free stay limits from flight data. Track your days spent in countries with rolling time windows (e.g., 90 days within 180 days) using your [Flighty](https://www.flightyapp.com/) export data.

## Features

✈️ **Track visa-free stays** - Monitor your days spent in countries with rolling window rules  
📊 **Detailed reports** - View all your stays with entry/exit dates and flight information  
🔮 **Future availability** - Calculate when you can return for desired stay durations  
🌍 **Multi-country support** - Works with any country's visa rules  
📱 **Flighty integration** - Uses CSV exports from the popular flight tracking app

## Use Cases

- **South Korea**: 90 days within 180 days (max 60 consecutive)
- **Schengen Area**: 90 days within 180 days
- **Japan**: 90 days within 180 days (on tourist waiver)
- **Any country**: Customize for any visa-free travel rules

## Requirements

- Python 3.9 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ivan-magda/days-of-stay.git
cd days-of-stay
```

## Getting Your Flight Data

1. Download [Flighty app](https://www.flightyapp.com/) (iOS)
2. Track your flights in the app
3. Export your data:
   - Open Flighty app
   - Go to Settings → Export Data
   - Choose "CSV Export"
   - Share/save the `FlightyExport-YYYY-MM-DD.csv` file

## Quick Start

### Analyze South Korea Stays

```shell script
# Use default CSV file (FlightyExport-2025-10-18.csv)
python analyze_korea_stay.py

# Or specify your own CSV file
python analyze_korea_stay.py -f FlightyExport-2025-11-20.csv
```


### Example Output

```
Analyzing visa-free stays: South Korea
======================================================================
Reference date: 2025-10-18
180-day window: 2025-04-22 to 2025-10-18

======================================================================

All South Korea stays:
======================================================================

Stay #1:
  Entry:  2025-05-01 - KE123 (LAX → ICN)
  Exit:   2025-05-15 - KE124 (ICN → LAX)
  Total stay: 15 days
  Days in window: 15 days ✓

Stay #2:
  Entry:  2025-08-10 - OZ456 (SFO → ICN)
  Exit:   2025-09-25 - OZ457 (ICN → SFO)
  Total stay: 47 days
  Days in window: 47 days ✓

======================================================================

📊 SUMMARY:
======================================================================
Total days in South Korea within rolling window: 62 days
Maximum allowed days: 90 days
Days remaining: 28 days

⚠️  Note: Single stay cannot exceed 60 days consecutively

✈️  If you fly to South Korea today (2025-10-18):
   You can stay for up to 28 days
   (Limited by: remaining days in 180-day window)

======================================================================

📅 FUTURE AVAILABILITY:
======================================================================

🎯 To stay 30 days:
   Wait until: 2025-11-03 (16 days from today)
   On that date, you will have used 60 days in the window
   Available for stay: 30 days (limited to 30 by consecutive rule)

🎯 To stay 60 days:
   Wait until: 2025-12-21 (64 days from today)
   On that date, you will have used 30 days in the window
   Available for stay: 60 days (limited to 60 by consecutive rule)
```


## Advanced Usage

### Generic Visa Analyzer

For other countries or custom rules, use the base `visa_stay_analyzer.py`:

```shell script
python visa_stay_analyzer.py \
  -f FlightyExport-2025-10-18.csv \
  -a ICN,GMP,CJU,PUS \
  -c "South Korea" \
  -w 180 \
  -m 90 \
  -x 60
```


#### Parameters

- `-f, --file`: Path to Flighty CSV export
- `-a, --airports`: Comma-separated airport codes (IATA)
- `-c, --country`: Country/region name for display
- `-w, --window`: Rolling window size in days
- `-m, --max-days`: Maximum days allowed in window
- `-x, --max-consecutive`: Maximum consecutive days (optional)
- `-d, --date`: Reference date (YYYY-MM-DD, default: today)

### More Examples

**Schengen Area:**
```shell script
python visa_stay_analyzer.py \
  -f flights.csv \
  -a CDG,AMS,FCO,MAD,BCN,FRA,MUC,VIE,ZRH \
  -c "Schengen" \
  -w 180 \
  -m 90
```


**Japan:**
```shell script
python visa_stay_analyzer.py \
  -f flights.csv \
  -a NRT,HND,KIX,NGO,FUK,CTS \
  -c "Japan" \
  -w 180 \
  -m 90
```


**Thailand (example with 30 consecutive day limit):**
```shell script
python visa_stay_analyzer.py \
  -f flights.csv \
  -a BKK,DMK,CNX,HKT,USM \
  -c "Thailand" \
  -w 180 \
  -m 90 \
  -x 30
```


**Historical analysis (specify date):**
```shell script
python visa_stay_analyzer.py \
  -f flights.csv \
  -a ICN,GMP \
  -c "South Korea" \
  -w 180 \
  -m 90 \
  -x 60 \
  -d 2025-06-01
```


## Creating Your Own Country Analyzer

You can create a custom script for any country by following the pattern in `analyze_korea_stay.py`:

```python
#!/usr/bin/env python3
import argparse
import os
from visa_stay_analyzer import analyze_visa_stays

# Define airport codes for your country
MY_COUNTRY_AIRPORTS = {
    'XXX',  # Main Airport
    'YYY',  # Secondary Airport
}

# Define visa rules
WINDOW_DAYS = 180
MAX_DAYS_IN_WINDOW = 90
MAX_CONSECUTIVE_DAYS = None  # or a number if applicable

def main():
    parser = argparse.ArgumentParser(
        description='Analyze My Country visa-free stays'
    )
    parser.add_argument('-f', '--file', default='FlightyExport-2025-10-18.csv',
                       help='Path to Flighty CSV export file')
    args = parser.parse_args()
    
    csv

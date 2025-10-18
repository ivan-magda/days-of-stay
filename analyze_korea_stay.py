#!/usr/bin/env python3
"""
Analyze South Korea stays from Flighty export data.
Uses the generic visa_stay_analyzer with Korea-specific parameters.
"""

import argparse
import os

from visa_stay_analyzer import analyze_visa_stays

# South Korean airport codes
KOREA_AIRPORTS = {
    'ICN',  # Incheon International Airport
    'GMP',  # Gimpo International Airport
    'CJU',  # Jeju International Airport
    'PUS',  # Gimhae International Airport (Busan)
    'KWJ',  # Gwangju Airport
    'TAE',  # Daegu International Airport
    'RSU',  # Yeosu Airport
    'USN',  # Ulsan Airport
    'KUV',  # Gunsan Airport
    'KPO',  # Pohang Airport
    'WJU',  # Wonju Airport
    'HIN',  # Sacheon Airport
    'MWX',  # Muan International Airport
    'KAG',  # Gangneung Airport
}

# South Korea visa-free stay rules
WINDOW_DAYS = 180
MAX_DAYS_IN_WINDOW = 90
MAX_CONSECUTIVE_DAYS = 60


def main():
    """Analyze South Korea stays using the base analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze South Korea visa-free stays from Flighty export data'
    )

    parser.add_argument(
        '-f', '--file',
        default='FlightyExport-2025-10-18.csv',
        help='Path to Flighty CSV export file (default: FlightyExport-2025-10-18.csv)'
    )

    args = parser.parse_args()

    # Get the CSV file path
    csv_path = args.file

    # If it's a relative path, make it relative to the script directory
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), csv_path)

    # Run analysis with Korea-specific parameters
    analyze_visa_stays(
        csv_path=csv_path,
        airport_codes=KOREA_AIRPORTS,
        country_name="South Korea",
        window_days=WINDOW_DAYS,
        max_days_in_window=MAX_DAYS_IN_WINDOW,
        max_consecutive_days=MAX_CONSECUTIVE_DAYS,
        reference_date=None  # Use today's date
    )


if __name__ == '__main__':
    main()

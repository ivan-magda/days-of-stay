#!/usr/bin/env python3
"""
Generic visa-free stay analyzer for flight data.
Analyzes stays in a country based on Flighty export data and visa rules.
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set


def parse_datetime(date_str: str) -> Optional[datetime]:
    """Parse datetime from various formats in the CSV."""
    if not date_str:
        return None

    try:
        return datetime.fromisoformat(date_str.replace('T', ' '))
    except (ValueError, AttributeError, TypeError):
        pass

    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def calculate_days_between(date1: Optional[datetime], date2: Optional[datetime]) -> int:
    """Calculate days between two dates (inclusive).
    
    Args:
        date1: Start date (should be <= date2)
        date2: End date (should be >= date1)
        
    Returns:
        Number of calendar days from date1 to date2 (inclusive).
        Returns 0 if either date is None or if date2 < date1.
    """
    if not date1 or not date2:
        return 0

    if date2 < date1:
        return 0

    delta = (date2.date() - date1.date()).days + 1
    return delta


def load_flights(csv_path: str, airport_codes: Set[str]) -> List[Dict]:
    """Load and filter flights from the CSV file.
    
    Args:
        csv_path: Path to Flighty CSV export
        airport_codes: Set of airport codes for the country to analyze
        
    Returns:
        List of flight dictionaries with entry/exit information
    """
    flights = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                from_airport = row['From']
                to_airport = row['To']
                canceled = row['Canceled'].lower() == 'true'

                if canceled:
                    continue

                # Check if this is entry or exit from the country
                is_arrival = to_airport in airport_codes and from_airport not in airport_codes
                is_departure = from_airport in airport_codes and to_airport not in airport_codes

                if is_arrival or is_departure:
                    gate_arrival = parse_datetime(row['Gate Arrival (Actual)']) or parse_datetime(
                        row['Landing (Actual)'])
                    gate_departure = parse_datetime(row['Gate Departure (Actual)']) or parse_datetime(
                        row['Take off (Actual)'])

                    flights.append({
                        'date': row['Date'],
                        'flight': f"{row['Airline']} {row['Flight']}",
                        'from': from_airport,
                        'to': to_airport,
                        'is_arrival': is_arrival,
                        'is_departure': is_departure,
                        'arrival_time': gate_arrival,
                        'departure_time': gate_departure,
                    })
    except FileNotFoundError:
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Sort by date
    flights.sort(key=lambda x: x['arrival_time'] if x['is_arrival'] else x['departure_time'])

    return flights


def calculate_stays(flights: List[Dict]) -> List[Dict]:
    """Calculate stays from flight entry/exit pairs.
    
    Args:
        flights: List of flight dictionaries
        
    Returns:
        List of stay dictionaries with entry and exit information
    """
    stays = []
    current_entry = None

    for flight in flights:
        if flight['is_arrival']:
            current_entry = flight
        elif flight['is_departure'] and current_entry:
            stays.append({
                'entry': current_entry,
                'exit': flight,
                'entry_date': current_entry['arrival_time'],
                'exit_date': flight['departure_time'],
            })
            current_entry = None

    return stays


def calculate_days_in_window(stays: List[Dict], window_start: datetime, window_end: datetime) -> int:
    """Calculate total days spent in country within a time window.
    
    Args:
        stays: List of stay dictionaries
        window_start: Start of the time window
        window_end: End of the time window
        
    Returns:
        Total number of days in the window
    """
    total_days = 0

    for stay in stays:
        entry_date = stay['entry_date']
        exit_date = stay['exit_date']

        window_entry = max(entry_date, window_start)
        window_exit = min(exit_date, window_end)

        if window_exit >= window_start and window_entry <= window_end:
            days = calculate_days_between(window_entry, window_exit)
            total_days += days

    return total_days


def print_stays_report(stays: List[Dict], window_start: datetime, today: datetime,
                       country_name: str):
    """Print detailed report of all stays."""
    print(f"All {country_name} stays:")
    print(f"{'=' * 70}")

    total_days_in_window = 0

    for i, stay in enumerate(stays, 1):
        entry_date = stay['entry_date']
        exit_date = stay['exit_date']

        # Calculate total days for this stay
        total_stay_days = calculate_days_between(entry_date, exit_date)

        # Calculate days within the window
        window_entry = max(entry_date, window_start)
        window_exit = min(exit_date, today)

        days_in_window = 0
        if window_exit >= window_start and window_entry <= today:
            days_in_window = calculate_days_between(window_entry, window_exit)

        in_window = days_in_window > 0

        print(f"\nStay #{i}:")
        print(
            f"  Entry:  {entry_date.strftime('%Y-%m-%d')} - {stay['entry']['flight']} ({stay['entry']['from']} → {stay['entry']['to']})")
        print(
            f"  Exit:   {exit_date.strftime('%Y-%m-%d')} - {stay['exit']['flight']} ({stay['exit']['from']} → {stay['exit']['to']})")
        print(f"  Total stay: {total_stay_days} days")

        if in_window:
            total_days_in_window += days_in_window
            if entry_date < window_start:
                print(
                    f"  Days in {window_start.strftime('%Y-%m-%d')} window: {days_in_window} days (from {window_entry.strftime('%Y-%m-%d')} to {window_exit.strftime('%Y-%m-%d')})")
            else:
                print(f"  Days in window: {days_in_window} days ✓")
        else:
            print(f"  Days in window: 0 days (outside window)")

    return total_days_in_window


def print_summary(total_days_in_window: int, max_days_in_window: int,
                  max_consecutive_days: int, today: datetime, country_name: str):
    """Print summary of visa status."""
    print(f"\n{'=' * 70}")
    print(f"\n📊 SUMMARY:")
    print(f"{'=' * 70}")
    print(f"Total days in {country_name} within rolling window: {total_days_in_window} days")
    print(f"Maximum allowed days: {max_days_in_window} days")
    print(f"Days remaining: {max_days_in_window - total_days_in_window} days")

    if max_consecutive_days:
        print(f"\n⚠️  Note: Single stay cannot exceed {max_consecutive_days} days consecutively")

    if total_days_in_window < max_days_in_window:
        remaining = max_days_in_window - total_days_in_window
        max_stay = min(remaining, max_consecutive_days) if max_consecutive_days else remaining

        print(f"\n✈️  If you fly to {country_name} today ({today.strftime('%Y-%m-%d')}):")
        print(f"   You can stay for up to {max_stay} days")

        if max_consecutive_days:
            limit_reason = f"{max_consecutive_days}-day consecutive stay rule" if max_stay == max_consecutive_days else "remaining days in window"
            print(f"   (Limited by: {limit_reason})")
    else:
        print(f"\n❌ You have exhausted your {max_days_in_window}-day limit within the window.")
        print(f"   You cannot enter {country_name} until some days expire from the window.")


def print_future_availability(stays: List[Dict], today: datetime, window_days: int,
                              max_days_in_window: int, max_consecutive_days: int,
                              total_days_in_window: int):
    """Print future availability for desired stay durations."""
    print(f"\n{'=' * 70}")
    print(f"\n📅 FUTURE AVAILABILITY:")
    print(f"{'=' * 70}")

    desired_stays = [30, 60] if max_consecutive_days >= 60 else [30]

    for desired_days in desired_stays:
        if desired_days > max_consecutive_days > 0:
            continue

        required_available = desired_days
        max_used_days = max_days_in_window - required_available

        if total_days_in_window <= max_used_days:
            print(f"\n✓ You can already stay {desired_days} days today!")
            continue

        # Simulate moving forward day by day to find when enough days expire
        found = False
        for days_forward in range(1, 365):
            future_date = today + timedelta(days=days_forward)
            future_window_start = future_date - timedelta(days=window_days - 1)

            # Recalculate days in window for that future date
            future_days = calculate_days_in_window(stays, future_window_start, future_date)

            if future_days <= max_used_days:
                available = max_days_in_window - future_days
                limited_to = min(available, max_consecutive_days) if max_consecutive_days else available

                print(f"\n🎯 To stay {desired_days} days:")
                print(f"   Wait until: {future_date.strftime('%Y-%m-%d')} ({days_forward} days from today)")
                print(f"   On that date, you will have used {future_days} days in the window")
                print(f"   Available for stay: {available} days (limited to {limited_to} by consecutive rule)")
                found = True
                break

        if not found:
            print(f"\n⚠️  Cannot calculate date for {desired_days}-day stay within next year")


def analyze_visa_stays(csv_path: str, airport_codes: Set[str], country_name: str,
                       window_days: int, max_days_in_window: int,
                       max_consecutive_days: int = None, reference_date: datetime = None):
    """Main analysis function.
    
    Args:
        csv_path: Path to Flighty CSV export
        airport_codes: Set of airport codes for the country
        country_name: Name of the country for display
        window_days: Size of rolling window (e.g., 180)
        max_days_in_window: Maximum days allowed in window (e.g., 90)
        max_consecutive_days: Maximum consecutive days per stay (optional)
        reference_date: Reference date for analysis (default: today)
    """
    if reference_date is None:
        reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    window_start = reference_date - timedelta(days=window_days - 1)

    print(f"Analyzing visa-free stays: {country_name}")
    print(f"{'=' * 70}")
    print(f"Reference date: {reference_date.strftime('%Y-%m-%d')}")
    print(f"{window_days}-day window: {window_start.strftime('%Y-%m-%d')} to {reference_date.strftime('%Y-%m-%d')}")
    print(f"\n{'=' * 70}\n")

    # Load and process flights
    flights = load_flights(csv_path, airport_codes)

    if not flights:
        print(f"No flights found to/from {country_name}")
        return

    # Calculate stays
    stays = calculate_stays(flights)

    if not stays:
        print(f"No completed stays found in {country_name}")
        return

    # Print detailed stays report
    total_days = print_stays_report(stays, window_start, reference_date, country_name)

    # Print summary
    print_summary(total_days, max_days_in_window, max_consecutive_days,
                  reference_date, country_name)

    # Print future availability
    print_future_availability(stays, reference_date, window_days, max_days_in_window,
                              max_consecutive_days or float('inf'), total_days)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Analyze visa-free stays from Flighty flight export data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze South Korea stays (90 days in 180, max 60 consecutive)
  %(prog)s -f flights.csv -a ICN,GMP,CJU,PUS -c "South Korea" -w 180 -m 90 -x 60
  
  # Analyze Schengen stays (90 days in 180)
  %(prog)s -f flights.csv -a CDG,AMS,FCO,MAD -c "Schengen" -w 180 -m 90
        """
    )

    parser.add_argument('-f', '--file', required=True,
                        help='Path to Flighty CSV export file')
    parser.add_argument('-a', '--airports', required=True,
                        help='Comma-separated list of airport codes (e.g., ICN,GMP,CJU)')
    parser.add_argument('-c', '--country', required=True,
                        help='Country/region name for display')
    parser.add_argument('-w', '--window', type=int, required=True,
                        help='Rolling window size in days (e.g., 180)')
    parser.add_argument('-m', '--max-days', type=int, required=True,
                        help='Maximum days allowed in window (e.g., 90)')
    parser.add_argument('-x', '--max-consecutive', type=int, default=None,
                        help='Maximum consecutive days per stay (optional)')
    parser.add_argument('-d', '--date', default=None,
                        help='Reference date for analysis (YYYY-MM-DD, default: today)')

    args = parser.parse_args()

    # Parse airport codes
    airport_codes = set(code.strip().upper() for code in args.airports.split(','))

    # Parse reference date if provided
    reference_date = None
    if args.date:
        try:
            reference_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    # Run analysis
    analyze_visa_stays(
        csv_path=args.file,
        airport_codes=airport_codes,
        country_name=args.country,
        window_days=args.window,
        max_days_in_window=args.max_days,
        max_consecutive_days=args.max_consecutive,
        reference_date=reference_date
    )


if __name__ == '__main__':
    main()

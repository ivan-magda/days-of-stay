# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Days of Stay Analyzer - A Python CLI tool to analyze visa-free stay limits from Flighty flight data exports. It tracks days spent in countries with rolling time windows (e.g., 90 days within 180 days).

## Running the Analyzers

```bash
# South Korea analyzer (uses preconfigured rules: 90 days in 180, max 60 consecutive)
uv run analyze-korea-stay
uv run analyze-korea-stay -f FlightyExport-2025-11-20.csv

# Generic analyzer for any country
uv run visa-stay-analyzer -f flights.csv -a ICN,GMP,CJU -c "South Korea" -w 180 -m 90 -x 60
```

## Architecture

**visa_stay_analyzer.py** - Core library with all analysis logic:

- `load_flights()` - Parses Flighty CSV exports, filters by airport codes
- `calculate_stays()` - Pairs entry/exit flights into stay records
- `calculate_days_in_window()` - Computes days spent within rolling window
- `analyze_visa_stays()` - Main API function, can be imported by country-specific scripts

**analyze_korea_stay.py** - Country-specific wrapper that imports `analyze_visa_stays()` with preconfigured South Korea parameters (airport codes, visa rules).

## Adding New Country Analyzers

Create a new file following `analyze_korea_stay.py` pattern:

1. Define airport codes set
2. Define visa rules (window_days, max_days, max_consecutive)
3. Call `analyze_visa_stays()` from visa_stay_analyzer

## Data Format

Expects Flighty CSV exports with columns: Date, Airline, Flight, From, To, Canceled, Gate Arrival (Actual), Gate Departure (Actual), Landing (Actual), Take off (Actual).

## Requirements

Python 3.9+, uv for package management. No external dependencies (stdlib only).

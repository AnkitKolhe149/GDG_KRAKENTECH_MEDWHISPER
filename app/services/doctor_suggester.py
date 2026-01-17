"""Simple doctor suggestion service loading a CSV and providing city-based suggestions."""
from pathlib import Path
import csv
from functools import lru_cache

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'doctors.csv'


@lru_cache(maxsize=1)
def load_doctors():
    doctors = []
    try:
        with DATA_FILE.open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize and parse numeric fields
                try:
                    row['rating'] = float(row.get('rating') or 0)
                except Exception:
                    row['rating'] = 0.0
                try:
                    row['years_of_experience'] = int(row.get('years_of_experience') or 0)
                except Exception:
                    row['years_of_experience'] = 0
                try:
                    row['consultation_fee_inr'] = int(row.get('consultation_fee_inr') or 0)
                except Exception:
                    row['consultation_fee_inr'] = 0
                # Keep original strings for others
                doctors.append(row)
    except FileNotFoundError:
        return []
    return doctors


def suggest_by_city(city: str, top_n: int = 5, min_fee: int | None = None, max_fee: int | None = None):
    """Return top_n doctors for the given city (case-insensitive), optionally filtered by fee range.

    Returns list of dicts with selected fields.
    """
    if not city:
        return []
    all_docs = load_doctors()
    city_lower = city.strip().lower()
    filtered = [d for d in all_docs if d.get('city') and d.get('city').strip().lower() == city_lower]

    # apply fee filtering if provided
    if min_fee is not None:
        try:
            min_fee_val = int(min_fee)
            filtered = [d for d in filtered if (d.get('consultation_fee_inr') is not None and int(d.get('consultation_fee_inr', 0)) >= min_fee_val)]
        except Exception:
            pass
    if max_fee is not None:
        try:
            max_fee_val = int(max_fee)
            filtered = [d for d in filtered if (d.get('consultation_fee_inr') is not None and int(d.get('consultation_fee_inr', 0)) <= max_fee_val)]
        except Exception:
            pass

    # sort by rating desc, then years_of_experience desc
    filtered.sort(key=lambda d: (d.get('rating', 0.0), d.get('years_of_experience', 0)), reverse=True)

    def _pick(d):
        return {
            'doctor_name': d.get('doctor_name'),
            'specialization': d.get('specialization'),
            'qualification': d.get('qualification'),
            'years_of_experience': d.get('years_of_experience'),
            'clinic_or_hospital': d.get('clinic_or_hospital'),
            'locality': d.get('locality'),
            'consultation_fee_inr': d.get('consultation_fee_inr'),
            'phone': d.get('phone'),
            'email': d.get('email'),
            'availability_days': d.get('availability_days'),
            'rating': d.get('rating'),
            'languages_spoken': d.get('languages_spoken'),
            'consultation_type': d.get('consultation_type')
        }

    return [_pick(d) for d in filtered[:top_n]]

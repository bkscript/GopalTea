"""
गोपाल चायवाला — बुकिंग रिपोर्ट स्क्रिप्ट

इस्तेमाल कैसे करें:
1. जो Google Form (बुकिंग/इनक्वायरी के लिए) बनाएंगे, उसकी Responses वाली
   Google Sheet को File > Download > CSV से डाउनलोड करें
2. उस फाइल का नाम "bookings.csv" रखें, इसी फोल्डर में रखें
3. टर्मिनल में चलाएं: python tools/booking_report.py

यह स्क्रिप्ट बताएगी:
- कुल कितनी बुकिंग/इनक्वायरी आईं
- किस पैकेज (ठेका / डे पैकेज / चारी सर्विस) की कितनी डिमांड है
- आने वाले (future) इवेंट्स की तारीखवार लिस्ट
"""

import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

CSV_FILE = Path(__file__).parent.parent / "bookings.csv"

# अगर आपकी Sheet के कॉलम नाम अलग हों, तो यहां बदल दें
COLUMN_MAP = {
    "name": "नाम",
    "phone": "फोन नंबर",
    "event_date": "इवेंट की तारीख",
    "package": "पैकेज चुनें",
}


def load_bookings(path: Path):
    if not path.exists():
        print(f"❌ फाइल नहीं मिली: {path}")
        print("पहले Google Sheet से CSV डाउनलोड करके 'bookings.csv' नाम से यहीं रखें।")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_date(value: str):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def main():
    rows = load_bookings(CSV_FILE)
    print(f"\n📋 कुल बुकिंग/इनक्वायरी: {len(rows)}\n")

    # पैकेज के हिसाब से गिनती
    package_col = COLUMN_MAP["package"]
    counts = Counter(row.get(package_col, "अज्ञात").strip() for row in rows)
    print("📦 पैकेज के हिसाब से डिमांड:")
    for pkg, count in counts.most_common():
        print(f"   {pkg}: {count}")

    # आने वाले इवेंट्स (आज या आगे की तारीख वाले)
    today = datetime.now()
    upcoming = []
    for row in rows:
        d = parse_date(row.get(COLUMN_MAP["event_date"], ""))
        if d and d >= today:
            upcoming.append((d, row))

    upcoming.sort(key=lambda x: x[0])

    print(f"\n📅 आने वाले इवेंट्स ({len(upcoming)}):")
    for d, row in upcoming:
        name = row.get(COLUMN_MAP["name"], "?")
        phone = row.get(COLUMN_MAP["phone"], "?")
        pkg = row.get(package_col, "?")
        print(f"   {d.strftime('%d-%m-%Y')} — {name} ({phone}) — {pkg}")

    print()


if __name__ == "__main__":
    main()
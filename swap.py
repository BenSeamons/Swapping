students = [
    {
        "id": "Ben",
        "clerkship_location": "Ft. Bragg",
        "clerkship_time": "Block 3-4",
        "trade_status": "willing",
        "contact_info": "ben@example.com"
    },
    {
        "id": "Alice",
        "clerkship_location": "San Antonio",
        "clerkship_time": "Block 3-4",
        "trade_status": "wanting",
        "contact_info": "alice@example.com"
    },
    {
        "id": "Charlie",
        "clerkship_location": "San Antonio",
        "clerkship_time": "Block 3-4",
        "trade_status": "no_trade",
        "contact_info": "charlie@example.com"
    },
    {
        "id": "Dana",
        "clerkship_location": "Ft. Bragg",
        "clerkship_time": "Block 3-4",
        "trade_status": "open",
        "contact_info": "dana@example.com"
    },
    # Add more students here
]

def find_matches(students):
    matches = []
    filtered = [s for s in students if s['trade_status'] != 'no_trade']

    index = {}
    for s in filtered:
        key = (s['clerkship_location'], s['clerkship_time'])
        index.setdefault(key, []).append(s)

    for key, group in index.items():
        willing = [s for s in group if s['trade_status'] == 'willing']
        wanting_or_open = [s for s in group if s['trade_status'] in ('wanting', 'open')]

        for w in willing:
            for wo in wanting_or_open:
                if w['id'] != wo['id']:
                    matches.append({
                        'student_1': w['id'],
                        'student_2': wo['id'],
                        'location': key[0],
                        'time': key[1],
                        'student_1_contact': w['contact_info'],
                        'student_2_contact': wo['contact_info']
                    })
    return matches

def categorize_candidate(candidate_status):
    if candidate_status == 'willing':
        return "🔥 Highest priority — willing to trade"
    elif candidate_status == 'wanting':
        return "⚡ High priority — wants to trade"
    elif candidate_status == 'open':
        return "✨ Medium priority — open to contact"
    else:
        return "❄️ Low priority — not trading"

def find_students_with_highlight(students, desired_location, desired_time):
    candidates = []
    for s in students:
        if s['clerkship_location'].lower() == desired_location.lower() and s['clerkship_time'].lower() == desired_time.lower():
            priority = categorize_candidate(s['trade_status'])
            candidates.append({
                'id': s['id'],
                'contact_info': s['contact_info'],
                'trade_status': s['trade_status'],
                'priority': priority
            })
    return candidates

# Example usage:

matches = find_matches(students)
print("🔗 Matches for trading:")
for match in matches:
    print(f"{match['student_1']} <--> {match['student_2']} at {match['location']} during {match['time']}")
    print(f"Contacts: {match['student_1']} ({match['student_1_contact']}), {match['student_2']} ({match['student_2_contact']})\n")

desired_location = "San Antonio"
desired_time = "Block 3-4"

print(f"📋 Students who have rotation at {desired_location} during {desired_time}:")
highlighted_candidates = find_students_with_highlight(students, desired_location, desired_time)
for c in highlighted_candidates:
    print(f"{c['id']} — {c['priority']} — Contact: {c['contact_info']}")

# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter

log_path = "log.txt"
stats_path = "bot_stats.json"
NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}
VEG = [1, 3, 5, 7]
MEAT = [2, 4, 6, 8]

def load_history():
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            c = f.read().strip()
            data = [int(x) for x in c.split(",") if x.strip().isdigit() and 1 <= int(x) <= 8]
            return data
    except:
        return []

def load_stats():
    if not os.path.exists(stats_path):
        return {'ok': 0, 'no': 0, 'total': 0, 'last_pred': None}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'ok': 0, 'no': 0, 'total': 0, 'last_pred': None}

def save_stats(stats):
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except:
        pass

def analyze(hist):
    if len(hist) < 30:
        return None
    freq = Counter(hist)
    last = hist[-1]
    last_two = (hist[-2], hist[-1]) if len(hist) >= 2 else None
    last_three = (hist[-3], hist[-2], hist[-1]) if len(hist) >= 3 else None
    
    after_single = defaultdict(Counter)
    for i in range(len(hist) - 1):
        after_single[hist[i]][hist[i+1]] += 1
    
    after_double = defaultdict(Counter)
    for i in range(len(hist) - 2):
        after_double[(hist[i], hist[i+1])][hist[i+2]] += 1
    
    after_triple = defaultdict(Counter)
    for i in range(len(hist) - 3):
        after_triple[(hist[i], hist[i+1], hist[i+2])][hist[i+3]] += 1
    
    scores = {}
    for num in range(1, 9):
        score = 0
        if last_three and last_three in after_triple:
            tc = after_triple[last_three].get(num, 0)
            tt = sum(after_triple[last_three].values())
            if tt > 0:
                score += (tc / tt) * 50
        if last_two and last_two in after_double:
            dc = after_double[last_two].get(num, 0)
            dt = sum(after_double[last_two].values())
            if dt > 0:
                score += (dc / dt) * 40
        if last in after_single:
            sc = after_single[last].get(num, 0)
            st = sum(after_single[last].values())
            if st > 0:
                score += (sc / st) * 30
        gp = freq.get(num, 0) / len(hist)
        score += gp * 10
        scores[num] = score
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top4 = ranked[:4]
    
    return {'top4': top4, 'freq': freq, 'after_triple': after_triple, 'last': last, 'last_three': last_three}

print("=" * 100)
print("BOT V5 - ADVANCED PATTERN ANALYZER (4 TARGETS + OK/NO)")
print("=" * 100)

last_len = 0
stats = load_stats()

while True:
    try:
        hist = load_history()
        if len(hist) > last_len:
            if last_len > 0 and len(hist) > last_len:
                actual = hist[-1]
                predicted = stats.get('last_pred')
                if predicted:
                    stats['total'] += 1
                    if predicted == actual:
                        stats['ok'] += 1
                        status = "[OK]"
                        beep_freq = 2000
                    else:
                        stats['no'] += 1
                        status = "[NO]"
                        beep_freq = 600
                    
                    accuracy = (stats['ok'] / stats['total'] * 100)
                    winsound.Beep(beep_freq, 100)
                    save_stats(stats)
            
            last_len = len(hist)
            res = analyze(hist)
            if res:
                top4 = res['top4']
                first_target = top4[0][0]
                targets_str = " | ".join([str(x[0]) for x in top4])
                
                accuracy = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
                status_display = "[OK]" if stats['total'] > 0 else ""
                
                if stats['total'] > 0:
                    if stats.get('last_pred') == hist[-2]:
                        status_display = "[OK]"
                    else:
                        status_display = "[NO]"
                
                print(f"Round {last_len}: {targets_str} {'.'*50} {status_display}")
                
                if stats['total'] % 100 == 0 and stats['total'] > 0:
                    print(f"\n{'='*100}")
                    print(f"SCORE: OK = {stats['ok']} | NO = {stats['no']} | Total = {stats['total']} | Accuracy = {accuracy:.2f}%")
                    print(f"{'='*100}\n")
                
                stats['last_pred'] = first_target
                save_stats(stats)
        
        time.sleep(0.3)
    
    except KeyboardInterrupt:
        print(f"\n\n{'='*100}")
        print("BOT STOPPED")
        if stats['total'] > 0:
            accuracy = (stats['ok'] / stats['total'] * 100)
            print(f"FINAL SCORE: OK = {stats['ok']} | NO = {stats['no']} | Total = {stats['total']}")
            print(f"ACCURACY = {accuracy:.2f}%")
        print(f"{'='*100}")
        break
    except Exception as err:
        pass

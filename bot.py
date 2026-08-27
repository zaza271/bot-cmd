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
        return {'correct': 0, 'total': 0, 'last_prediction': None}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'correct': 0, 'total': 0, 'last_prediction': None}

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
        gp = freq.get(num, 0) / len(hist) if len(hist) > 0 else 0
        score += gp * 10
        scores[num] = score
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top4 = ranked[:4]
    total = sum(s for _, s in top4)
    conf = (total / sum(scores.values()) * 100) if sum(scores.values()) > 0 else 0
    
    return {
        'top4': top4,
        'conf': conf,
        'freq': freq,
        'after_triple': after_triple,
        'last': last,
        'last_two': last_two,
        'last_three': last_three
    }

print("=" * 100)
print("ADVANCED PATTERN ANALYZER BOT - V3 (With Accuracy Tracking)")
print("=" * 100)

last_len = 0
stats = load_stats()

while True:
    try:
        hist = load_history()
        if len(hist) > last_len:
            if last_len > 0 and len(hist) > last_len:
                actual = hist[-1]
                predicted = stats.get('last_prediction')
                if predicted:
                    stats['total'] = stats.get('total', 0) + 1
                    if predicted == actual:
                        stats['correct'] = stats.get('correct', 0) + 1
                        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                        print(f"\n✓ CORRECT! Predicted: {predicted} ({NAMES[predicted]}) = Actual: {actual} ({NAMES[actual]})")
                        print(f"✓ SCORE: {stats['correct']}/{stats['total']} | Accuracy: {accuracy:.1f}%")
                        winsound.Beep(2000, 200)
                    else:
                        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                        print(f"\n✗ WRONG! Predicted: {predicted} ({NAMES[predicted]}) != Actual: {actual} ({NAMES[actual]})")
                        print(f"✗ SCORE: {stats['correct']}/{stats['total']} | Accuracy: {accuracy:.1f}%")
                        winsound.Beep(600, 150)
            
            last_len = len(hist)
            res = analyze(hist)
            
            if res:
                top4 = res['top4']
                conf = res['conf']
                freq = res['freq']
                after_triple = res['after_triple']
                last = res['last']
                last_two = res['last_two']
                last_three = res['last_three']
                
                top4_str = "".join([str(x[0]) for x in top4])
                first_target = top4[0][0] if top4 else None
                
                print(f"\n[Round: {last_len}] Last: {last} ({NAMES[last]})")
                if last_three:
                    print(f"Last Three: {last_three[0]} -> {last_three[1]} -> {last_three[2]}")
                print(f"NEXT PREDICTION: >>> {top4_str} <<<")
                print("+" + "=" * 98 + "+")
                print("RANK |  NUM  |  SCORE  |  NAME           | TYPE  |  NEXT PREDICTION")
                print("+" + "=" * 98 + "+")
                
                for rank, (item, score) in enumerate(top4, 1):
                    itype = "VEG " if item in VEG else "MEAT"
                    marker = "[PREDICTED]" if rank == 1 else ""
                    print(f"  {rank}    |   {item:2d}   |  {score:6.2f}  |  {NAMES[item]:15s} | {itype} |  {marker}")
                
                print("+" + "=" * 98 + "+")
                print(f"Overall Confidence: {conf:.1f}%")
                
                if first_target == 2:
                    print("\n[ALERT] CHICK (2) IS PRIMARY TARGET!!!")
                    winsound.Beep(1200, 150)
                elif first_target == 6:
                    print("\n[ALERT] FISH (6) IS PRIMARY TARGET!!!")
                    winsound.Beep(800, 200)
                
                if conf > 60:
                    print(f"[CRITICAL] VERY HIGH CONFIDENCE: {conf:.1f}%")
                    winsound.Beep(2000, 100)
                
                meat_in_top4 = sum(1 for x, _ in top4 if x in MEAT)
                veg_in_top4 = sum(1 for x, _ in top4 if x in VEG)
                print(f"[INFO] Top 4: {veg_in_top4} VEG + {meat_in_top4} MEAT")
                
                print("\nPATTERN ANALYSIS (Last Triple):")
                print("-" * 100)
                if last_three and last_three in after_triple and after_triple[last_three]:
                    print(f"After Pattern {last_three[0]}-{last_three[1]}-{last_three[2]}:")
                    top_after = sorted(after_triple[last_three].items(), key=lambda x: x[1], reverse=True)[:6]
                    for rank, (num, count) in enumerate(top_after, 1):
                        itype = "[VEG]" if num in VEG else "[MEAT]"
                        pred_marker = " <-- NEXT PREDICTION" if rank == 1 else ""
                        print(f"  {rank}. {num} ({NAMES[num]:10s}): {count:4d} times {itype}{pred_marker}")
                
                print("\nGENERAL FREQUENCY:")
                print("-" * 100)
                for i in range(1, 9):
                    count = freq.get(i, 0)
                    pct = (count / last_len * 100) if last_len > 0 else 0
                    bar = "*" * int(pct / 2)
                    in_top = "★ " if any(x == i for x, _ in top4) else "  "
                    itype = "VEG" if i in VEG else "MEAT"
                    print(f"{in_top}{itype} {i} ({NAMES[i]:10s}): {count:5d} ({pct:6.2f}%) {bar}")
                
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"\n[STATS] Correct: {stats['correct']}/{stats['total']} | Accuracy: {accuracy:.1f}%")
                print("=" * 100)
                
                stats['last_prediction'] = first_target
                save_stats(stats)
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nBot stopped. Goodbye!")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)

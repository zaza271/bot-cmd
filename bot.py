# -*- coding: utf-8 -*-
import os, time, winsound
from collections import defaultdict, Counter

log_path = "log.txt"
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
    except Exception as e:
        print(f"[ERROR] Cannot read log: {e}")
        return []

def analyze_optimized(hist):
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
            triple_count = after_triple[last_three].get(num, 0)
            triple_total = sum(after_triple[last_three].values())
            if triple_total > 0:
                score += (triple_count / triple_total) * 50
        
        if last_two and last_two in after_double:
            double_count = after_double[last_two].get(num, 0)
            double_total = sum(after_double[last_two].values())
            if double_total > 0:
                score += (double_count / double_total) * 40
        
        if last in after_single:
            single_count = after_single[last].get(num, 0)
            single_total = sum(after_single[last].values())
            if single_total > 0:
                score += (single_count / single_total) * 30
        
        general_prob = freq.get(num, 0) / len(hist) if len(hist) > 0 else 0
        score += general_prob * 10
        
        scores[num] = score
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top4 = ranked[:4]
    
    total_score = sum(s for _, s in top4)
    confidence = (total_score / sum(scores.values()) * 100) if sum(scores.values()) > 0 else 0
    
    return {
        'top4': top4,
        'confidence': confidence,
        'freq': freq,
        'after_single': after_single,
        'after_double': after_double,
        'after_triple': after_triple,
        'last': last,
        'last_two': last_two,
        'last_three': last_three,
    }

def beep_alert(alert_type):
    if alert_type == "CHICK":
        for _ in range(3):
            winsound.Beep(1200, 150)
            time.sleep(0.1)
    elif alert_type == "FISH":
        for _ in range(2):
            winsound.Beep(800, 200)
            time.sleep(0.15)
    elif alert_type == "HIGH_CONFIDENCE":
        winsound.Beep(1500, 300)
    elif alert_type == "CRITICAL":
        for _ in range(4):
            winsound.Beep(2000, 100)
            time.sleep(0.05)

print("=" * 95)
print("ADVANCED PATTERN ANALYZER BOT - V2 (Pattern Focused)")
print("=" * 95)

last_len = 0
while True:
    try:
        hist = load_history()
        if len(hist) > last_len and len(hist) >= 30:
            last_len = len(hist)
            res = analyze_optimized(hist)
            if res:
                top4 = res['top4']
                conf = res['confidence']
                freq = res['freq']
                after_triple = res['after_triple']
                last = res['last']
                last_two = res['last_two']
                last_three = res['last_three']
                
                top4_str = "".join([str(item) for item, _ in top4])
                first_target = top4[0][0] if top4 else None
                
                print(f"\n[Round: {last_len}]  Last: {last} ({NAMES[last]})")
                if last_two:
                    print(f"Last Two: {last_two[0]} -> {last_two[1]}")
                if last_three:
                    print(f"Last Three: {last_three[0]} -> {last_three[1]} -> {last_three[2]}")
                print(f"TARGETS: >>> {top4_str} <<<")
                
                print("+" + "=" * 93 + "+")
                print("RANK |  NUMBER  |  SCORE  |  NAME           | TYPE")
                print("+" + "=" * 93 + "+")
                
                for rank, (item, score) in enumerate(top4, 1):
                    item_type = "VEG" if item in VEG else "MEAT"
                    strategy = "PRIMARY" if rank == 1 else "SECONDARY" if rank == 2 else "BACKUP" if rank == 3 else "FALLBACK"
                    print(f"  {rank}    |   {item:2d}    |  {score:6.2f}  |  {NAMES[item]:15s} | {item_type}")
                
                print("+" + "=" * 93 + "+")
                print(f"Overall Confidence: {conf:.1f}%")
                
                print("\n*** ALERT SYSTEM ***")
                if first_target == 2:
                    print("[ALERT] CHICK (2) IS PRIMARY TARGET!!!")
                    beep_alert("CHICK")
                elif first_target == 6:
                    print("[ALERT] FISH (6) IS PRIMARY TARGET!!!")
                    beep_alert("FISH")
                
                if conf > 60:
                    print(f"[CRITICAL] VERY HIGH CONFIDENCE: {conf:.1f}%")
                    beep_alert("CRITICAL")
                elif conf > 50:
                    print(f"[HIGH] High Confidence: {conf:.1f}%")
                    beep_alert("HIGH_CONFIDENCE")
                
                meat_in_top4 = sum(1 for item, _ in top4 if item in MEAT)
                veg_in_top4 = sum(1 for item, _ in top4 if item in VEG)
                print(f"[INFO] Top 4: {veg_in_top4} Vegetables + {meat_in_top4} Meat")
                
                if 2 in [item for item, _ in top4]:
                    print("[WATCH] CHICK (2) appears in top 4!")
                if 6 in [item for item, _ in top4]:
                    print("[WATCH] FISH (6) appears in top 4!")
                
                print("\nPATTERN ANALYSIS:")
                print("-" * 95)
                
                if last_three and last_three in after_triple and after_triple[last_three]:
                    print(f"TRIPLE: {last_three[0]}-{last_three[1]}-{last_three[2]}")
                    top_after_triple = sorted(after_triple[last_three].items(), key=lambda x: x[1], reverse=True)[:5]
                    for num, count in top_after_triple:
                        item_type = "[VEG]" if num in VEG else "[MEAT]"
                        print(f"  -> {num} ({NAMES[num]}): {count} times {item_type}")
                
                print("\nGENERAL FREQUENCY:")
                print("-" * 95)
                for i in range(1, 9):
                    count = freq.get(i, 0)
                    percentage = (count / last_len * 100) if last_len > 0 else 0
                    bar = "*" * int(percentage / 2)
                    in_top4 = "STAR" if any(item == i for item, _ in top4) else "    "
                    item_type = "VEG" if i in VEG else "MEAT"
                    print(f"{in_top4} {item_type} Number {i} ({NAMES[i]:10s}): {count:5d} | {percentage:6.2f}% {bar}")
                
                print("\n" + "=" * 95 + "\n")
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nBot stopped. Goodbye!")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)

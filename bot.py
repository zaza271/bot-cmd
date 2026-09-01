# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter

log_path = "log.txt"
stats_path = "bot_stats.json"
ok_results_path = "ok.txt"
no_results_path = "no.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}

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
        return {'ok': 0, 'no': 0, 'total': 0}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'ok': 0, 'no': 0, 'total': 0}

def save_stats(stats):
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except:
        pass

def save_ok_result(rnd, pred, actual, confidence):
    try:
        with open(ok_results_path, "a", encoding="utf-8") as f:
            f.write(f"Round {rnd} | Predicted={pred}({NAMES[pred]}) | Actual={actual}({NAMES[actual]}) | Conf={confidence:.1f}%\n")
    except:
        pass

def save_no_result(rnd, pred, actual, confidence):
    try:
        with open(no_results_path, "a", encoding="utf-8") as f:
            f.write(f"Round {rnd} | Predicted={pred}({NAMES[pred]}) | Actual={actual}({NAMES[actual]}) | Conf={confidence:.1f}%\n")
    except:
        pass

class AIPredictor:
    def __init__(self):
        pass
    
    def markov_3(self, hist):
        """تحليل 3 أرقام سابقة"""
        chains = defaultdict(Counter)
        for i in range(len(hist) - 3):
            key = (hist[i], hist[i+1], hist[i+2])
            chains[key][hist[i+3]] += 1
        return chains
    
    def markov_2(self, hist):
        """تحليل رقمين سابقين"""
        chains = defaultdict(Counter)
        for i in range(len(hist) - 2):
            key = (hist[i], hist[i+1])
            chains[key][hist[i+2]] += 1
        return chains
    
    def markov_1(self, hist):
        """تحليل رقم واحد سابق"""
        chains = defaultdict(Counter)
        for i in range(len(hist) - 1):
            chains[hist[i]][hist[i+1]] += 1
        return chains
    
    def predict(self, hist):
        """التنبؤ للجولة التالية"""
        if len(hist) < 50:
            return None, 0
        
        last = hist[-1]
        last_two = (hist[-2], hist[-1])
        last_three = (hist[-3], hist[-2], hist[-1])
        
        scores = {i: 0 for i in range(1, 9)}
        
        # Markov 3 (50% وزن)
        m3 = self.markov_3(hist)
        if last_three in m3:
            total = sum(m3[last_three].values())
            for num in range(1, 9):
                scores[num] += (m3[last_three].get(num, 0) / total) * 50
        
        # Markov 2 (35% وزن)
        m2 = self.markov_2(hist)
        if last_two in m2:
            total = sum(m2[last_two].values())
            for num in range(1, 9):
                scores[num] += (m2[last_two].get(num, 0) / total) * 35
        
        # Markov 1 (15% وزن)
        m1 = self.markov_1(hist)
        if last in m1:
            total = sum(m1[last].values())
            for num in range(1, 9):
                scores[num] += (m1[last].get(num, 0) / total) * 15
        
        # ترتيب أفضل 4
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top4 = ranked[:4]
        
        total_score = sum(s for _, s in top4)
        confidence = (total_score / 100) if total_score > 0 else 0
        
        return top4, confidence

print("=" * 130)
print("🤖 AI BOT V9 - FIXED PREDICTION LOGIC")
print("=" * 130)

stats = load_stats()
predictor = AIPredictor()
hist = load_history()

if len(hist) < 50:
    print(f"❌ خطأ: البيانات قليلة ({len(hist)} جولة)")
    exit()

print(f"✓ تم التحميل: {len(hist)} جولة")
print(f"✓ النتائج الصحيحة: {ok_results_path}")
print(f"✓ النتائج الخاطئة: {no_results_path}\n")
print("=" * 130 + "\n")

last_len = len(hist)
next_prediction = None
next_confidence = 0

while True:
    try:
        hist = load_history()
        
        # إذا كانت هناك جولة جديدة
        if len(hist) > last_len:
            actual_result = hist[-1]  # النتيجة الفعلية للجولة الجديدة
            
            # تحقق من التنبؤ السابق
            if next_prediction is not None:
                if next_prediction == actual_result:
                    stats['ok'] += 1
                    status = "✓ OK"
                    save_ok_result(last_len, next_prediction, actual_result, next_confidence)
                    winsound.Beep(2000, 100)
                else:
                    stats['no'] += 1
                    status = "✗ NO"
                    save_no_result(last_len, next_prediction, actual_result, next_confidence)
                    winsound.Beep(600, 100)
                
                stats['total'] += 1
                save_stats(stats)
                
                accuracy = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"Round {last_len:7d}: Predicted={next_prediction}({NAMES[next_prediction]}) | Actual={actual_result}({NAMES[actual_result]}) | {status} | Acc={accuracy:.2f}%")
            
            last_len = len(hist)
        
        # التنبؤ للجولة التالية
        top4, confidence = predictor.predict(hist)
        
        if top4:
            next_prediction = top4[0][0]
            next_confidence = confidence * 100
            targets_str = " | ".join([str(x[0]) for x in top4])
            conf_bar = "█" * int(confidence * 20)
            
            print(f"Next Round {len(hist) + 1}: Targets={targets_str:<15} | Conf={confidence*100:5.1f}% {conf_bar:<20}")
            
            if stats['total'] % 50 == 0 and stats['total'] > 0:
                acc = (stats['ok'] / stats['total'] * 100)
                print("-" * 130)
                print(f"📊 STATS: ✓ OK={stats['ok']:6d} | ✗ NO={stats['no']:6d} | Total={stats['total']:7d} | Accuracy={acc:.2f}%")
                print("-" * 130)
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 130)
        print("🛑 BOT STOPPED")
        if stats['total'] > 0:
            acc = (stats['ok'] / stats['total'] * 100)
            print(f"✓ Final: OK={stats['ok']} | ✗ NO={stats['no']} | Total={stats['total']} | Accuracy={acc:.2f}%")
        print("=" * 130)
        break
    except Exception as err:
        print(f"Error: {err}")
        time.sleep(1)

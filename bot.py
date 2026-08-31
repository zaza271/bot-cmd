# -*- coding: utf-8 -*-
import os, time, winsound, json, math
from collections import defaultdict, Counter

log_path = "log.txt"
stats_path = "bot_stats.json"
ok_results_path = "ok.txt"
no_results_path = "no.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}

def load_history():
    if not os.path.exists(log_path):
        print(f"❌ خطأ: لم أجد الملف '{log_path}'")
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            c = f.read().strip()
            data = [int(x) for x in c.split(",") if x.strip().isdigit() and 1 <= int(x) <= 8]
            return data
    except Exception as err:
        print(f"❌ خطأ في قراءة الملف: {err}")
        return []

def load_stats():
    if not os.path.exists(stats_path):
        return {'ok': 0, 'no': 0, 'total': 0, 'last_pred': None, 'last_confidence': 0}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'ok': 0, 'no': 0, 'total': 0, 'last_pred': None, 'last_confidence': 0}

def save_stats(stats):
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except:
        pass

def save_ok_result(rnd, pred, actual, confidence):
    """حفظ النتائج الصحيحة في ok.txt"""
    try:
        with open(ok_results_path, "a", encoding="utf-8") as f:
            f.write(f"Round {rnd} | Predicted={pred}({NAMES[pred]}) | Actual={actual}({NAMES[actual]}) | Confidence={confidence:.2f}%\n")
    except:
        pass

def save_no_result(rnd, pred, actual, confidence):
    """حفظ النتائج الخاطئة في no.txt"""
    try:
        with open(no_results_path, "a", encoding="utf-8") as f:
            f.write(f"Round {rnd} | Predicted={pred}({NAMES[pred]}) | Actual={actual}({NAMES[actual]}) | Confidence={confidence:.2f}%\n")
    except:
        pass

class AIPredictor:
    def __init__(self):
        self.weights = {i: 1.0 for i in range(1, 9)}
    
    def markov_analysis(self, hist, order=3):
        chains = defaultdict(Counter)
        if order == 3 and len(hist) >= 4:
            for i in range(len(hist) - 3):
                key = (hist[i], hist[i+1], hist[i+2])
                chains[key][hist[i+3]] += 1
        elif order == 2 and len(hist) >= 3:
            for i in range(len(hist) - 2):
                key = (hist[i], hist[i+1])
                chains[key][hist[i+2]] += 1
        elif order == 1 and len(hist) >= 2:
            for i in range(len(hist) - 1):
                chains[hist[i]][hist[i+1]] += 1
        return chains
    
    def get_probabilities(self, hist, last_three, last_two, last):
        probs = {i: 0 for i in range(1, 9)}
        
        chains_3 = self.markov_analysis(hist, order=3)
        if last_three in chains_3:
            total = sum(chains_3[last_three].values())
            for num in range(1, 9):
                count = chains_3[last_three].get(num, 0)
                probs[num] += (count / total * 50)
        
        chains_2 = self.markov_analysis(hist, order=2)
        if last_two in chains_2:
            total = sum(chains_2[last_two].values())
            for num in range(1, 9):
                count = chains_2[last_two].get(num, 0)
                probs[num] += (count / total * 35)
        
        chains_1 = self.markov_analysis(hist, order=1)
        if last in chains_1:
            total = sum(chains_1[last].values())
            for num in range(1, 9):
                count = chains_1[last].get(num, 0)
                probs[num] += (count / total * 15)
        
        return probs
    
    def frequency_analysis(self, hist):
        freq = Counter(hist)
        total = len(hist)
        freq_probs = {}
        
        for num in range(1, 9):
            count = freq.get(num, 0)
            freq_probs[num] = (count / total * 100) if total > 0 else 0
        
        return freq_probs
    
    def gap_analysis(self, hist):
        gap_scores = {}
        current_pos = len(hist)
        
        for num in range(1, 9):
            positions = [i for i, x in enumerate(hist) if x == num]
            if positions:
                last_pos = positions[-1]
                gap = current_pos - last_pos
                gap_scores[num] = min(gap / len(hist) * 100, 100)
            else:
                gap_scores[num] = 100
        
        return gap_scores
    
    def predict(self, hist):
        if len(hist) < 50:
            return None, 0
        
        last = hist[-1]
        last_two = (hist[-2], hist[-1]) if len(hist) >= 2 else None
        last_three = (hist[-3], hist[-2], hist[-1]) if len(hist) >= 3 else None
        
        probs = self.get_probabilities(hist, last_three, last_two, last)
        freq_probs = self.frequency_analysis(hist)
        gap_scores = self.gap_analysis(hist)
        
        predictions = {}
        for num in range(1, 9):
            score = probs.get(num, 0) * 0.6 + freq_probs.get(num, 0) * 0.25 + gap_scores.get(num, 0) * 0.15
            predictions[num] = score * self.weights[num]
        
        ranked = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        top4 = ranked[:4]
        
        total_score = sum(s for _, s in top4)
        confidence = (total_score / sum(predictions.values()) * 100) if sum(predictions.values()) > 0 else 0
        
        return top4, confidence

print("=" * 140)
print("🤖 AI PREDICTOR BOT V8 - FIXED RESULTS")
print("=" * 140)

stats = load_stats()
predictor = AIPredictor()

hist = load_history()

if len(hist) < 50:
    print(f"❌ خطأ: البيانات قليلة ({len(hist)} جولة). المطلوب 50 جولة على الأقل!")
    exit()

print(f"✓ تم التحميل: {len(hist)} جولة من '{log_path}'")
print(f"✓ النتائج الصحيحة ستُحفظ في: {ok_results_path}")
print(f"✓ النتائج الخاطئة ستُحفظ في: {no_results_path}\n")
print("=" * 140 + "\n")

last_len = len(hist)
last_predicted_round = -1
last_predicted_value = None
last_predicted_confidence = 0

while True:
    try:
        hist = load_history()
        
        # إذا كانت هناك جولة جديدة، تحقق من النتيجة السابقة
        if len(hist) > last_len:
            actual = hist[-1]
            
            # التحقق: هل كان لدينا توقع للجولة السابقة؟
            if last_predicted_round == last_len - 1:
                # نعم، تحقق من صحة التوقع
                if last_predicted_value == actual:
                    stats['ok'] += 1
                    status = "✓ OK"
                    save_ok_result(last_len - 1, last_predicted_value, actual, last_predicted_confidence)
                    winsound.Beep(2000, 100)
                else:
                    stats['no'] += 1
                    status = "✗ NO"
                    save_no_result(last_len - 1, last_predicted_value, actual, last_predicted_confidence)
                    winsound.Beep(600, 100)
                
                stats['total'] += 1
                save_stats(stats)
            
            last_len = len(hist)
        
        # التنبؤ للجولة الحالية
        top4, confidence = predictor.predict(hist)
        
        if top4:
            first_target = top4[0][0]
            targets_str = " | ".join([str(x[0]) for x in top4])
            
            accuracy = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_display = ""
            
            if stats['total'] > 0 and len(hist) > last_predicted_round:
                if last_predicted_round >= 0 and last_predicted_value == hist[last_predicted_round]:
                    status_display = "✓ OK"
                elif last_predicted_round >= 0:
                    status_display = "✗ NO"
            
            conf_bar = "█" * int(confidence / 5)
            print(f"Round {len(hist):7d} | Targets: {targets_str:<15} | Conf: {confidence:6.2f}% {conf_bar:<20} | {status_display:>10}")
            
            if stats['total'] % 50 == 0 and stats['total'] > 0:
                print("-" * 140)
                print(f"📊 STATS: ✓ OK={stats['ok']:6d} | ✗ NO={stats['no']:6d} | Total={stats['total']:7d} | Accuracy={accuracy:.2f}%")
                print(f"📁 Files: {ok_results_path} | {no_results_path}")
                print("-" * 140)
            
            # حفظ التوقع الحالي للجولة التالية
            last_predicted_round = len(hist)
            last_predicted_value = first_target
            last_predicted_confidence = confidence
        
        time.sleep(0.2)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 140)
        print("🛑 BOT STOPPED")
        if stats['total'] > 0:
            accuracy = (stats['ok'] / stats['total'] * 100)
            print(f"📊 FINAL: ✓ OK={stats['ok']} | ✗ NO={stats['no']} | Total={stats['total']} | Accuracy={accuracy:.2f}%")
            print(f"✓ النتائج الصحيحة محفوظة في: {ok_results_path}")
            print(f"✗ النتائج الخاطئة محفوظة في: {no_results_path}")
        print("=" * 140)
        break
    except Exception as err:
        print(f"❌ Error: {err}")
        time.sleep(1)

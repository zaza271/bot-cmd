# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter

log_path = "log.txt"
stats_path = "bot_stats.json"
ok_path = "ok.txt"
no_path = "no.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}

def read_log():
    """قراءة البيانات من log.txt"""
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = [int(x.strip()) for x in f.read().split(",") if x.strip().isdigit() and 1 <= int(x) <= 8]
            return data
    except:
        return []

def load_stats():
    """تحميل الإحصائيات"""
    if not os.path.exists(stats_path):
        return {'ok': 0, 'no': 0, 'total': 0}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'ok': 0, 'no': 0, 'total': 0}

def save_stats(stats):
    """حفظ الإحصائيات"""
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except:
        pass

def save_ok(round_num, predicted, actual, conf):
    """حفظ النتيجة الصحيحة"""
    try:
        with open(ok_path, "a", encoding="utf-8") as f:
            f.write(f"Round {round_num}: Predicted={predicted}({NAMES[predicted]}) | Actual={actual}({NAMES[actual]}) | Conf={conf:.1f}%\n")
    except:
        pass

def save_no(round_num, predicted, actual, conf):
    """حفظ النتيجة الخاطئة"""
    try:
        with open(no_path, "a", encoding="utf-8") as f:
            f.write(f"Round {round_num}: Predicted={predicted}({NAMES[predicted]}) | Actual={actual}({NAMES[actual]}) | Conf={conf:.1f}%\n")
    except:
        pass

class Predictor:
    """نظام التنبؤ"""
    
    def predict_next(self, data):
        """التنبؤ بالرقم التالي"""
        if len(data) < 50:
            return None, 0, None
        
        # الأرقام الثلاثة الأخيرة
        last_3 = (data[-3], data[-2], data[-1])
        last_2 = (data[-2], data[-1])
        last_1 = data[-1]
        
        scores = {i: 0.0 for i in range(1, 9)}
        
        # تحليل Markov من 3 أرقام (50%)
        count_3 = defaultdict(int)
        for i in range(len(data) - 3):
            if (data[i], data[i+1], data[i+2]) == last_3:
                count_3[data[i+3]] += 1
        
        if count_3:
            total = sum(count_3.values())
            for num in range(1, 9):
                scores[num] += (count_3[num] / total) * 50
        
        # تحليل Markov من رقمين (35%)
        count_2 = defaultdict(int)
        for i in range(len(data) - 2):
            if (data[i], data[i+1]) == last_2:
                count_2[data[i+2]] += 1
        
        if count_2:
            total = sum(count_2.values())
            for num in range(1, 9):
                scores[num] += (count_2[num] / total) * 35
        
        # تحليل Markov من رقم واحد (15%)
        count_1 = defaultdict(int)
        for i in range(len(data) - 1):
            if data[i] == last_1:
                count_1[data[i+1]] += 1
        
        if count_1:
            total = sum(count_1.values())
            for num in range(1, 9):
                scores[num] += (count_1[num] / total) * 15
        
        # ترتيب النتائج
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top4 = sorted_scores[:4]
        
        # الثقة (من أفضل توقع)
        confidence = top4[0][1] if top4 else 0
        predicted = top4[0][0] if top4 else None
        
        return predicted, confidence, top4

print("=" * 140)
print("🤖 BOT MEAT V10 - CORRECTED")
print("=" * 140)

predictor = Predictor()
stats = load_stats()
data = read_log()

if len(data) < 50:
    print(f"❌ خطأ: البيانات قليلة ({len(data)} رقم). المطلوب 50 على الأقل!")
    exit()

print(f"✓ تم تحميل {len(data)} رقم من {log_path}\n")

last_data_len = len(data)
last_pred = None
last_conf = 0
predictions_count = 0

while True:
    try:
        data = read_log()
        
        # إذا ظهرت أرقام جديدة
        if len(data) > last_data_len:
            actual = data[-1]  # آخر رقم ظهر
            
            # تحقق من التنبؤ السابق
            if last_pred is not None:
                if last_pred == actual:
                    stats['ok'] += 1
                    status = "✓ OK"
                    save_ok(last_data_len, last_pred, actual, last_conf)
                    winsound.Beep(2000, 100)
                else:
                    stats['no'] += 1
                    status = "✗ NO"
                    save_no(last_data_len, last_pred, actual, last_conf)
                    winsound.Beep(600, 100)
                
                stats['total'] += 1
                save_stats(stats)
                
                acc = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"Round {last_data_len:7d}: Pred={last_pred} | Actual={actual} | {status} | Acc={acc:.2f}%")
            
            last_data_len = len(data)
        
        # التنبؤ بالرقم التالي
        pred, conf, top4 = predictor.predict_next(data)
        
        if pred:
            targets_str = " | ".join([str(x[0]) for x in top4])
            conf_bar = "█" * int(conf * 20)
            
            print(f"Next: Targets={targets_str:<20} | Conf={conf*100:5.1f}% {conf_bar:<20}")
            
            last_pred = pred
            last_conf = conf * 100
            predictions_count += 1
            
            if stats['total'] % 50 == 0 and stats['total'] > 0:
                acc = (stats['ok'] / stats['total'] * 100)
                print("-" * 140)
                print(f"📊 ✓ OK={stats['ok']:6d} | ✗ NO={stats['no']:6d} | Total={stats['total']:7d} | Accuracy={acc:.2f}%")
                print("-" * 140)
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 140)
        print("🛑 STOPPED")
        if stats['total'] > 0:
            acc = (stats['ok'] / stats['total'] * 100)
            print(f"✓ RESULTS: OK={stats['ok']} | ✗ NO={stats['no']} | Total={stats['total']} | Accuracy={acc:.2f}%")
            print(f"📁 Files: {ok_path} | {no_path}")
        print("=" * 140)
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)

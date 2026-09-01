# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter
import statistics

log_path = "text.log"
stats_path = "bot_stats.json"
ok_path = "ok.txt"
no_path = "no.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}

def read_log():
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # إزالة المسافات والفواصل الإضافية
            data = [int(x.strip()) for x in content.replace(" ", "").split(",") 
                    if x.strip().isdigit() and 1 <= int(x.strip()) <= 8]
            return data
    except Exception as e:
        print(f"خطأ في القراءة: {e}")
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

def save_result(file_path, round_num, predicted, actual, conf):
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Round {round_num}: Pred={predicted}({NAMES[predicted]}) | Actual={actual}({NAMES[actual]}) | Conf={conf:.1f}%\n")
    except:
        pass

class DataAnalyzer:
    """تحليل البيانات الحقيقية"""
    
    def __init__(self, data):
        self.data = data
        self.freq = Counter(data)
        self.total = len(data)
        
        # حساب الإحصائيات
        print("\n" + "=" * 150)
        print("📊 تحليل البيانات:")
        print("=" * 150)
        for num in range(1, 9):
            count = self.freq[num]
            percent = (count / self.total * 100)
            bar = "█" * int(percent / 2)
            print(f"الرقم {num} ({NAMES[num]:10s}): {count:6d} مرة ({percent:5.2f}%) {bar}")
        print("=" * 150 + "\n")

class SmartPredictor:
    """نظام تنبؤ ذكي بناءً على البيانات الحقيقية"""
    
    def __init__(self, data):
        self.data = data
        self.build_chains()
    
    def build_chains(self):
        """بناء سلاسل ماركوف من البيانات الحقيقية"""
        # ماركوف 3
        self.m3 = defaultdict(Counter)
        for i in range(len(self.data) - 3):
            key = (self.data[i], self.data[i+1], self.data[i+2])
            self.m3[key][self.data[i+3]] += 1
        
        # ماركوف 2
        self.m2 = defaultdict(Counter)
        for i in range(len(self.data) - 2):
            key = (self.data[i], self.data[i+1])
            self.m2[key][self.data[i+2]] += 1
        
        # ماركوف 1
        self.m1 = defaultdict(Counter)
        for i in range(len(self.data) - 1):
            self.m1[self.data[i]][self.data[i+1]] += 1
    
    def get_scores(self, data_slice):
        """حساب الدرجات بناءً على الأنماط الحقيقية"""
        if len(data_slice) < 3:
            return None
        
        last_3 = (data_slice[-3], data_slice[-2], data_slice[-1])
        last_2 = (data_slice[-2], data_slice[-1])
        last_1 = data_slice[-1]
        
        scores = {i: 0.0 for i in range(1, 9)}
        
        # ماركوف 3 (50%)
        if last_3 in self.m3:
            total = sum(self.m3[last_3].values())
            for num in range(1, 9):
                count = self.m3[last_3].get(num, 0)
                if count > 0:
                    scores[num] += (count / total) * 50
        
        # ماركوف 2 (30%)
        if last_2 in self.m2:
            total = sum(self.m2[last_2].values())
            for num in range(1, 9):
                count = self.m2[last_2].get(num, 0)
                if count > 0:
                    scores[num] += (count / total) * 30
        
        # ماركوف 1 (20%)
        if last_1 in self.m1:
            total = sum(self.m1[last_1].values())
            for num in range(1, 9):
                count = self.m1[last_1].get(num, 0)
                if count > 0:
                    scores[num] += (count / total) * 20
        
        return scores
    
    def predict(self, data_slice):
        """التنبؤ بأفضل 4 أرقام"""
        if len(data_slice) < 50:
            return None, 0, None
        
        scores = self.get_scores(data_slice)
        if not scores:
            return None, 0, None
        
        # تطبيع الدرجات
        total_score = sum(scores.values())
        if total_score > 0:
            for num in range(1, 9):
                scores[num] = (scores[num] / total_score) * 100
        
        # اختيار أفضل 4
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top4 = ranked[:4]
        
        predicted = top4[0][0]
        confidence = top4[0][1]
        
        return predicted, confidence, top4

print("=" * 150)
print("🤖 SMART PREDICTOR BOT V13 - تحليل 36,000 نتيجة حقيقية")
print("=" * 150)

# قراءة البيانات
data = read_log()

if len(data) < 50:
    print(f"❌ خطأ: البيانات قليلة ({len(data)} رقم)")
    exit()

print(f"\n✓ تم تحميل {len(data):,} رقم من text.log\n")

# تحليل البيانات
analyzer = DataAnalyzer(data)

# إنشاء المنبئ
predictor = SmartPredictor(data)

stats = load_stats()
last_data_len = len(data)
last_pred = None
last_conf = 0
check_round = 0

print("🚀 البوت يعمل الآن...\n")

while True:
    try:
        data = read_log()
        
        # إذا ظهر رقم جديد
        if len(data) > last_data_len:
            actual = data[-1]
            
            # التحقق من التنبؤ السابق
            if last_pred is not None and check_round > 0:
                if last_pred == actual:
                    stats['ok'] += 1
                    status = "✓ OK"
                    file_to_save = ok_path
                    beep_freq = 2000
                else:
                    stats['no'] += 1
                    status = "✗ NO"
                    file_to_save = no_path
                    beep_freq = 600
                
                stats['total'] += 1
                save_result(file_to_save, check_round, last_pred, actual, last_conf)
                save_stats(stats)
                winsound.Beep(beep_freq, 150)
                
                acc = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"Round {check_round:7d}: Pred={last_pred}({NAMES[last_pred]}) | Actual={actual}({NAMES[actual]}) | {status} | Acc={acc:.2f}%")
            
            last_data_len = len(data)
            check_round = last_data_len - 1
        
        # التنبؤ
        pred, conf, top4 = predictor.predict(data)
        
        if pred and top4:
            targets_str = " | ".join([f"{x[0]}" for x in top4])
            conf_bar = "█" * int(conf / 5)
            
            print(f"Next Round {len(data) + 1:7d}: Targets={targets_str:<20} | Conf={conf:6.2f}% {conf_bar:<20}")
            
            last_pred = pred
            last_conf = conf
            
            # إحصائيات
            if stats['total'] % 100 == 0 and stats['total'] > 0:
                acc = (stats['ok'] / stats['total'] * 100)
                print("=" * 150)
                print(f"📊 STATS: ✓ OK={stats['ok']:7d} | ✗ NO={stats['no']:7d} | Total={stats['total']:8d} | Accuracy={acc:.2f}%")
                print("=" * 150)
        
        time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 150)
        print("🛑 BOT STOPPED")
        if stats['total'] > 0:
            acc = (stats['ok'] / stats['total'] * 100)
            print(f"✓ FINAL:")
            print(f"  ✓ OK = {stats['ok']}")
            print(f"  ✗ NO = {stats['no']}")
            print(f"  Total = {stats['total']}")
            print(f"  Accuracy = {acc:.2f}%")
        print("=" * 150)
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)

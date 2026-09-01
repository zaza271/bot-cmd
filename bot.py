# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter
from collections import deque

log_path = "log.txt"
stats_path = "bot_stats.json"
win_path = "wins.txt"
loss_path = "losses.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}

def read_log():
    """قراءة البيانات من log.txt"""
    if not os.path.exists(log_path):
        print(f"❌ لم أجد الملف: {log_path}")
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            content = content.lstrip(',').strip()
            data = []
            for item in content.split(","):
                item = item.strip()
                if item.isdigit():
                    num = int(item)
                    if 1 <= num <= 8:
                        data.append(num)
            return data
    except Exception as e:
        print(f"❌ خطأ في القراءة: {e}")
        return []

def load_stats():
    if not os.path.exists(stats_path):
        return {'wins': 0, 'losses': 0, 'total': 0}
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {'wins': 0, 'losses': 0, 'total': 0}

def save_stats(stats):
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except:
        pass

def save_result(file_path, round_num, predicted, actual, conf, status):
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Round {round_num}: Pred={predicted}({NAMES[predicted]}) | Actual={actual}({NAMES[actual]}) | Conf={conf:.2f}% | {status}\n")
    except:
        pass

class AdaptivePredictor:
    """منبئ ديناميكي يتعلم من آخر 300 نتيجة فقط"""
    
    def __init__(self, data, window_size=300):
        self.window_size = window_size
        self.data = deque(data[-window_size:], maxlen=window_size)
        self.rebuild_chains()
    
    def rebuild_chains(self):
        """إعادة بناء سلاسل ماركوف من البيانات الحالية"""
        data_list = list(self.data)
        
        # ماركوف 3
        self.m3 = defaultdict(Counter)
        for i in range(len(data_list) - 3):
            key = (data_list[i], data_list[i+1], data_list[i+2])
            self.m3[key][data_list[i+3]] += 1
        
        # ماركوف 2
        self.m2 = defaultdict(Counter)
        for i in range(len(data_list) - 2):
            key = (data_list[i], data_list[i+1])
            self.m2[key][data_list[i+2]] += 1
        
        # ماركوف 1
        self.m1 = defaultdict(Counter)
        for i in range(len(data_list) - 1):
            self.m1[data_list[i]][data_list[i+1]] += 1
        
        # التكرار الأساسي
        self.freq = Counter(data_list)
        self.total = len(data_list)
    
    def add_data(self, num):
        """إضافة نتيجة جديدة وإعادة التدريب"""
        self.data.append(num)
        self.rebuild_chains()
    
    def get_scores(self, data_list):
        """حساب الدرجات بناءً على الأنماط الحالية"""
        if len(data_list) < 3:
            return None
        
        last_3 = (data_list[-3], data_list[-2], data_list[-1])
        last_2 = (data_list[-2], data_list[-1])
        last_1 = data_list[-1]
        
        scores = {i: 0.0 for i in range(1, 9)}
        
        # ماركوف 3 (50%)
        if last_3 in self.m3:
            total = sum(self.m3[last_3].values())
            if total > 0:
                for num in range(1, 9):
                    count = self.m3[last_3].get(num, 0)
                    if count > 0:
                        scores[num] += (count / total) * 50
        
        # ماركوف 2 (30%)
        if last_2 in self.m2:
            total = sum(self.m2[last_2].values())
            if total > 0:
                for num in range(1, 9):
                    count = self.m2[last_2].get(num, 0)
                    if count > 0:
                        scores[num] += (count / total) * 30
        
        # ماركوف 1 (20%)
        if last_1 in self.m1:
            total = sum(self.m1[last_1].values())
            if total > 0:
                for num in range(1, 9):
                    count = self.m1[last_1].get(num, 0)
                    if count > 0:
                        scores[num] += (count / total) * 20
        
        return scores
    
    def predict(self):
        """التنبؤ بناءً على البيانات الحالية فقط"""
        data_list = list(self.data)
        
        if len(data_list) < 50:
            return None, 0
        
        scores = self.get_scores(data_list)
        if not scores:
            return None, 0
        
        # تطبيع الدرجات
        total_score = sum(scores.values())
        if total_score > 0:
            for num in range(1, 9):
                scores[num] = (scores[num] / total_score) * 100
        else:
            return None, 0
        
        # اختيار الأقوى
        best_num = max(scores.items(), key=lambda x: x[1])
        predicted = best_num[0]
        confidence = best_num[1]
        
        return predicted, confidence

print("=" * 150)
print("🤖 ADAPTIVE PREDICTOR BOT - استراتيجية ديناميكية ذكية")
print("=" * 150)

# قراءة البيانات
data = read_log()

if len(data) < 50:
    print(f"❌ خطأ: البيانات قليلة ({len(data)} رقم). المطلوب 50 على الأقل!")
    exit()

print(f"\n✓ تم تحميل {len(data):,} رقم من log.txt")
print(f"✓ التدريب على آخر 300 نتيجة فقط (نافذة متحركة)\n")

# إنشاء المنبئ الديناميكي
predictor = AdaptivePredictor(data, window_size=300)

stats = load_stats()
last_data_len = len(data)
last_pred = None
last_conf = 0
check_round = 0
consecutive_losses = 0

print("🚀 البوت يعمل الآن (تعلم ديناميكي)...\n")

while True:
    try:
        data = read_log()
        
        # إذا ظهر رقم جديد
        if len(data) > last_data_len:
            actual = data[-1]
            
            # التحقق من التنبؤ السابق
            if last_pred is not None and check_round > 0:
                if last_pred == actual:
                    stats['wins'] += 1
                    status = "✓ WIN"
                    file_to_save = win_path
                    beep_freq = 2000
                    beep_duration = 200
                    consecutive_losses = 0
                else:
                    stats['losses'] += 1
                    status = "✗ LOSS"
                    file_to_save = loss_path
                    beep_freq = 600
                    beep_duration = 150
                    consecutive_losses += 1
                
                stats['total'] += 1
                save_result(file_to_save, check_round, last_pred, actual, last_conf, status)
                save_stats(stats)
                winsound.Beep(beep_freq, beep_duration)
                
                win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"Round {check_round:7d}: Pred={last_pred}({NAMES[last_pred]}) | Actual={actual}({NAMES[actual]}) | {status} | Rate={win_rate:.2f}%")
                
                # إذا 5 خسائر متتالية - تحذير
                if consecutive_losses >= 5:
                    print(f"⚠️  تحذير: {consecutive_losses} خسائر متتالية! قد يكون النمط قد تغير")
                    consecutive_losses = 0
            
            # إضافة النتيجة الجديدة للتدريب
            predictor.add_data(actual)
            
            last_data_len = len(data)
            check_round = last_data_len - 1
        
        # التنبؤ
        pred, conf = predictor.predict()
        
        if pred is not None:
            conf_bar = "█" * int(conf / 5)
            status_icon = "✓ GO" if conf >= 85 else "⚠️  CAUTION"
            print(f"Next Round {len(data) + 1:7d}: Predict={pred}({NAMES[pred]}) | Conf={conf:6.2f}% {conf_bar:<20} {status_icon}")
            
            last_pred = pred
            last_conf = conf
        else:
            print(f"Next Round {len(data) + 1:7d}: ⊘ INSUFFICIENT DATA")
            last_pred = None
            last_conf = 0
        
        # إحصائيات كل 100 نتيجة
        if stats['total'] % 100 == 0 and stats['total'] > 0:
            win_rate = (stats['wins'] / stats['total'] * 100)
            print("=" * 150)
            print(f"📊 ADAPTIVE STATS: ✓ WINS={stats['wins']:6d} | ✗ LOSSES={stats['losses']:6d} | Total={stats['total']:7d} | Win Rate={win_rate:.2f}%")
            print(f"🔄 التدريب على: {len(predictor.data)} نتيجة حديثة")
            print("=" * 150)
        
        time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 150)
        print("🛑 BOT STOPPED")
        if stats['total'] > 0:
            win_rate = (stats['wins'] / stats['total'] * 100)
            print(f"✓ FINAL RESULTS:")
            print(f"  ✓ WINS   = {stats['wins']}")
            print(f"  ✗ LOSSES = {stats['losses']}")
            print(f"  Total    = {stats['total']}")
            print(f"  Win Rate = {win_rate:.2f}%")
            print(f"\n📁 Results saved in:")
            print(f"  ✓ wins.txt")
            print(f"  ✗ losses.txt")
        print("=" * 150)
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(1)

# -*- coding: utf-8 -*-
import os, time, winsound, json
from collections import defaultdict, Counter
import statistics
import math

log_path = "log"  # بدون .txt
stats_path = "bot_stats.json"
results_path = "results.txt"

NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}
VEG = [1, 3, 5, 7]
MEAT = [2, 4, 6, 8]

def load_history():
    if not os.path.exists(log_path):
        print(f"❌ خطأ: لم أجد الملف '{log_path}'")
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            c = f.read().strip()
            data = [int(x) for x in c.split(",") if x.strip().isdigit() and 1 <= int(x) <= 8]
            print(f"✓ تم تحميل {len(data)} جولة من الملف '{log_path}'")
            return data
    except Exception as err:
        print(f"❌ خطأ في قراءة الملف: {err}")
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

def save_result(rnd, pred, actual, status):
    try:
        with open(results_path, "a", encoding="utf-8") as f:
            result_mark = "✓ OK" if status == "OK" else "✗ NO"
            f.write(f"Round {rnd}: Predicted={pred}({NAMES[pred]}) | Actual={actual}({NAMES[actual]}) | {result_mark}\n")
    except:
        pass

def analyze_advanced(hist):
    """تحليل متقدم مع خوارزميات رياضية"""
    if len(hist) < 50:
        return None
    
    freq = Counter(hist)
    last = hist[-1]
    
    # 1. تحليل الأنماط الثلاثية (Triple Pattern Analysis)
    after_triple = defaultdict(Counter)
    for i in range(len(hist) - 3):
        triple = (hist[i], hist[i+1], hist[i+2])
        after_triple[triple][hist[i+3]] += 1
    
    # 2. تحليل الأنماط الثنائية (Double Pattern Analysis)
    after_double = defaultdict(Counter)
    for i in range(len(hist) - 2):
        double = (hist[i], hist[i+1])
        after_double[double][hist[i+2]] += 1
    
    # 3. تحليل الأنماط الفردية (Single Pattern Analysis)
    after_single = defaultdict(Counter)
    for i in range(len(hist) - 1):
        after_single[hist[i]][hist[i+1]] += 1
    
    # 4. تحليل التكرار (Frequency Analysis)
    repeat_count = {}
    for num in range(1, 9):
        repeat_count[num] = freq.get(num, 0)
    
    # 5. تحليل الانحراف المعياري (Standard Deviation)
    freq_values = list(freq.values())
    mean_freq = statistics.mean(freq_values) if freq_values else 0
    std_dev = statistics.stdev(freq_values) if len(freq_values) > 1 else 0
    
    # 6. تحليل الفترات الزمنية (Gap Analysis)
    last_positions = {}
    for num in range(1, 9):
        positions = [i for i, x in enumerate(hist) if x == num]
        if positions:
            last_positions[num] = len(hist) - positions[-1]
        else:
            last_positions[num] = len(hist)
    
    # حساب النقاط لكل رقم
    scores = {}
    last_two = (hist[-2], hist[-1]) if len(hist) >= 2 else None
    last_three = (hist[-3], hist[-2], hist[-1]) if len(hist) >= 3 else None
    
    for num in range(1, 9):
        score = 0
        
        # نقاط من النمط الثلاثي (50%)
        if last_three and last_three in after_triple:
            triple_count = after_triple[last_three].get(num, 0)
            triple_total = sum(after_triple[last_three].values())
            if triple_total > 0:
                triple_prob = (triple_count / triple_total) * 100
                score += triple_prob * 0.5
        
        # نقاط من النمط الثنائي (30%)
        if last_two and last_two in after_double:
            double_count = after_double[last_two].get(num, 0)
            double_total = sum(after_double[last_two].values())
            if double_total > 0:
                double_prob = (double_count / double_total) * 100
                score += double_prob * 0.3
        
        # نقاط من النمط الفردي (15%)
        if last in after_single:
            single_count = after_single[last].get(num, 0)
            single_total = sum(after_single[last].values())
            if single_total > 0:
                single_prob = (single_count / single_total) * 100
                score += single_prob * 0.15
        
        # نقاط من التكرار العام (5%)
        general_prob = (repeat_count[num] / len(hist)) * 100
        score += general_prob * 0.05
        
        scores[num] = score
    
    # ترتيب أفضل 4 توقعات
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top4 = ranked[:4]
    
    return {
        'top4': top4,
        'scores': scores,
        'freq': freq,
        'last': last,
        'last_two': last_two,
        'last_three': last_three,
        'after_triple': after_triple,
        'gap': last_positions
    }

print("=" * 130)
print("🎯 PROFESSIONAL BOT - ADVANCED PATTERN ANALYZER V6")
print("خوارزميات: التحليل الثلاثي + الثنائي + الفردي + التكرار + الانحراف المعياري + تحليل الفترات")
print("=" * 130)

last_len = 0
stats = load_stats()

# تحميل البيانات
hist = load_history()

if len(hist) < 50:
    print(f"❌ خطأ: البيانات قليلة جداً ({len(hist)} جولة). المطلوب 50 جولة على الأقل!")
    exit()

print(f"✓ تم التحميل بنجاح! البيانات: {len(hist)} جولة\n")
print("=" * 130)

last_len = len(hist)
last_check = len(hist)

while True:
    try:
        # فحص إذا كانت هناك بيانات جديدة
        hist = load_history()
        
        if len(hist) > last_len:
            # فحص النتيجة السابقة
            actual = hist[-1]
            predicted = stats.get('last_pred')
            if predicted:
                stats['total'] += 1
                if predicted == actual:
                    stats['ok'] += 1
                    status = "✓ OK"
                    beep = 2000
                else:
                    stats['no'] += 1
                    status = "✗ NO"
                    beep = 600
                
                acc = (stats['ok'] / stats['total'] * 100)
                save_result(last_len, predicted, actual, status)
                winsound.Beep(beep, 100)
                save_stats(stats)
            
            last_len = len(hist)
        
        # التحليل المتقدم كل 5 جولات
        if len(hist) % 5 == 0 and len(hist) > last_check:
            last_check = len(hist)
            
            res = analyze_advanced(hist)
            
            if res:
                top4 = res['top4']
                first_target = top4[0][0]
                targets_str = " | ".join([f"{x[0]} ({NAMES[x[0]][:4]})" for x in top4])
                
                accuracy = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
                status_display = ""
                
                if stats['total'] > 0 and len(hist) > 1:
                    if stats.get('last_pred') == hist[-2]:
                        status_display = "✓ OK"
                    else:
                        status_display = "✗ NO"
                
                # الطباعة الاحترافية
                print(f"Round {len(hist):6d} | Targets: {targets_str:<40} | {status_display:>10}")
                
                # طباعة الإحصائيات كل 50 جولة
                if stats['total'] % 50 == 0 and stats['total'] > 0:
                    print("-" * 130)
                    print(f"📊 STATS: ✓ OK={stats['ok']:5d} | ✗ NO={stats['no']:5d} | Total={stats['total']:6d} | Accuracy={accuracy:.2f}%")
                    print("-" * 130)
                
                stats['last_pred'] = first_target
                save_stats(stats)
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 130)
        print("🛑 BOT STOPPED")
        if stats['total'] > 0:
            accuracy = (stats['ok'] / stats['total'] * 100)
            print(f"📊 FINAL SCORE: ✓ OK = {stats['ok']} | ✗ NO = {stats['no']} | Total = {stats['total']}")
            print(f"🎯 ACCURACY = {accuracy:.2f}%")
            print(f"📁 النتائج محفوظة في: {results_path}")
        print("=" * 130)
        break
    except Exception as err:
        print(f"Error: {err}")
        time.sleep(1)

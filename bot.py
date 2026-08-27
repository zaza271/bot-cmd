# -*- coding: utf-8 -*-
import os, time, winsound
from collections import defaultdict, Counter

log_path = "log.txt"
NAMES = {1: "Corn", 2: "Chick", 3: "Tomato", 4: "Cow", 5: "Chili", 6: "Fish", 7: "Carrot", 8: "Shrimp"}
VEG = [1, 3, 5, 7]
MEAT = [2, 4, 6, 8]
ALL = list(range(1, 9))

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

def analyze(hist):
    if len(hist) < 30:
        return None

    total = len(hist)
    freq = Counter(hist)
    
    # حساب التكرارات الفعلية من السجل
    freq_prob = {i: freq.get(i, 0) / total for i in ALL}

    gaps = {}
    for i in ALL:
        gap = 0
        for x in reversed(hist):
            if x == i:
                break
            gap += 1
        gaps[i] = gap
    max_gap = max(gaps.values()) if gaps else 1
    gap_norm = {i: gaps[i] / max_gap for i in ALL}

    last = hist[-1]
    
    # 1. انتقالات الدرجة الأولى
    trans1 = defaultdict(Counter)
    for a, b in zip(hist, hist[1:]):
        trans1[a][b] += 1
    trans1_prob = {i: 0 for i in ALL}
    if last in trans1:
        total_last = sum(trans1[last].values())
        if total_last > 0:
            for i in ALL:
                trans1_prob[i] = trans1[last].get(i, 0) / total_last

    # 2. انتقالات الدرجة الثانية
    last_pair = (hist[-2], hist[-1]) if len(hist) >= 2 else None
    trans2 = defaultdict(Counter)
    for i in range(len(hist)-2):
        a, b, c = hist[i], hist[i+1], hist[i+2]
        trans2[(a, b)][c] += 1
    trans2_prob = {i: 0 for i in ALL}
    if last_pair and last_pair in trans2:
        total_pair = sum(trans2[last_pair].values())
        if total_pair > 0:
            for i in ALL:
                trans2_prob[i] = trans2[last_pair].get(i, 0) / total_pair

    # 3. تأثير الخضر على اللحوم
    veg_to_meat = defaultdict(lambda: defaultdict(int))
    for i in range(1, len(hist)):
        if hist[i-1] in VEG and hist[i] in MEAT:
            veg_to_meat[hist[i-1]][hist[i]] += 1

    # 4. سلاسل الخضر الطويلة
    veg_streak_to_meat = defaultdict(lambda: defaultdict(int))
    for i in range(2, len(hist)):
        if hist[i] in MEAT and hist[i-1] in VEG and hist[i-2] in VEG:
            veg_streak_to_meat[(hist[i-2], hist[i-1])][hist[i]] += 1

    # حساب السكور الأساسي لكل عنصر
    score = {}
    for i in ALL:
        boost_veg = 0.0
        if last in VEG and i in MEAT:
            vc = veg_to_meat[last].get(i, 0)
            tv = sum(veg_to_meat[last].values())
            if tv > 0:
                boost_veg = vc / tv

        boost_streak = 0.0
        if last_pair and last_pair[0] in VEG and last_pair[1] in VEG and i in MEAT:
            pc = veg_streak_to_meat[last_pair].get(i, 0)
            tp = sum(veg_streak_to_meat[last_pair].values())
            if tp > 0:
                boost_streak = pc / tp

        # الأوزان الأصلية
        s = (0.15 * freq_prob.get(i, 0) +
             0.10 * gap_norm.get(i, 0) +
             0.25 * trans1_prob.get(i, 0) +
             0.20 * trans2_prob.get(i, 0) +
             0.25 * boost_veg +
             0.05 * boost_streak)
        score[i] = s

    total_score = sum(score.values())
    if total_score == 0:
        return None

    score_norm = {i: (score[i] / total_score) * 100 for i in ALL}
    
    # ========== استراتيجية القنص المتوازن ==========
    # نختار من الخضر والحوم بشكل متوازن
    veg_scores = [(i, score_norm[i]) for i in VEG]
    meat_scores = [(i, score_norm[i]) for i in MEAT]
    
    veg_scores.sort(key=lambda x: x[1], reverse=True)
    meat_scores.sort(key=lambda x: x[1], reverse=True)
    
    # نختار أفضل خضرتين وأفضل لحمتين
    top2_veg = veg_scores[:2] if len(veg_scores) >= 2 else veg_scores
    top2_meat = meat_scores[:2] if len(meat_scores) >= 2 else meat_scores
    
    # دمج النتائج الـ 4 الأفضل
    balanced_top4 = top2_veg + top2_meat
    balanced_top4.sort(key=lambda x: x[1], reverse=True)
    
    confidence = sum(p for _, p in balanced_top4)
    meat_in_top4 = len(top2_meat)
    veg_in_top4 = len(top2_veg)

    return {
        'top4': balanced_top4,
        'confidence': confidence,
        'strong': (confidence > 40.0),
        'meat_count': meat_in_top4,
        'veg_count': veg_in_top4,
        'last': last,
        'all_scores': score_norm,
    }

def beep_alert():
    """تنبيه صوتي"""
    winsound.Beep(1000, 200)

# ---------- التشغيل ----------
print("=" * 85)
print("🎯 SMART PREDICTOR BOT - BALANCED HUNTING (خضر ولحوم متوازن 2:2)")
print("=" * 85)

last_len = 0
while True:
    try:
        hist = load_history()
        if len(hist) > last_len and len(hist) >= 30:
            last_len = len(hist)
            res = analyze(hist)
            if res:
                top4 = res['top4']
                conf = res['confidence']
                strong = res['strong']
                meat_cnt = res['meat_count']
                veg_cnt = res['veg_count']
                last = res['last']
                all_scores = res['all_scores']
                top4_str = "".join([str(item) for item, _ in top4])

                print(f"\n[📊 Round: {last_len}]  Last: {last} ({NAMES[last]})  |  🎯 TARGETS: >>> {top4_str} <<<")
                print("+" + "=" * 83 + "+")
                print("🏆 RANK |  ITEM        |  PROB %  |  TYPE           | STRATEGY")
                print("+" + "=" * 83 + "+")
                
                for rank, (item, prob) in enumerate(top4, 1):
                    itype = "🌿 Vegetable" if item in VEG else "🥩 Meat"
                    strategy = "PRIMARY 🎯" if rank == 1 else "SECONDARY 🔄" if rank == 2 else "BACKUP 🛡️" if rank == 3 else "FALLBACK ⚠️"
                    
                    print(f"  {rank}    |  {item:2d} ({NAMES[item]:7s})  |  {prob:6.2f}%  |  {itype:15s} | {strategy}")
                
                print("+" + "=" * 83 + "+")
                
                # عرض الإحصائيات
                print(f"📈 CONFIDENCE: {conf:.1f}% | MEAT: {meat_cnt}/2 | VEG: {veg_cnt}/2 | STRENGTH: {'💪 STRONG' if strong else '⚠️ MEDIUM'}")
                
                # استراتيجيات القنص المتقدمة
                print("\n🎯 HUNTING STATUS:")
                print(f"   ✅ متوازن تماماً: {veg_cnt} خضر + {meat_cnt} لحم = 4 خيارات مثالي")
                
                if conf > 50:
                    print(f"   🔥 ثقة عالية جداً: {conf:.1f}%")
                    winsound.Beep(1200, 300)
                elif conf > 40:
                    print(f"   ⚡ ثقة جيدة: {conf:.1f}%")
                    beep_alert()
                
                # عرض جميع الاحتمالات
                print("\n📊 ALL ITEMS ANALYSIS:")
                print("-" * 65)
                for i in ALL:
                    bar_len = int(all_scores[i] / 2)
                    bar = "█" * bar_len
                    itype = "🌿" if i in VEG else "🥩"
                    in_top4 = "⭐" if any(item == i for item, _ in top4) else "  "
                    print(f"{in_top4} {itype} Item {i} ({NAMES[i]:7s}): {all_scores[i]:6.2f}% {bar}")
                
                print("\n" + "=" * 85 + "\n")
        
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n👋 البوت توقف. وداعاً!")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)

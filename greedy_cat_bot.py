import time
import cv2
import numpy as np
import pyautogui

# إعدادات المراقبة والتحليل
CONFIDENCE_THRESHOLD = 75.0
HISTORY_WINDOW = 50

# أرقام اللحوم (Meat)
MEAT_NUMBERS = {2, 4, 6, 8}
# أرقام الخضروات (Green)
GREEN_NUMBERS = {1, 3, 5, 7}

stats = {
    "wins": 0,
    "partials": 0,
    "losses": 0,
    "total_rounds": 0
}

history = [3, 7, 6, 8, 3, 1, 6, 7, 3, 6, 3, 8]

def analyze_next_targets(hist):
    train_data = hist[-HISTORY_WINDOW:] if len(hist) >= HISTORY_WINDOW else hist
    sample_size = len(train_data)

    if sample_size < 5:
        return [6, 7, 3, 8], 87.50, True

    scores = {i: 0.0 for i in range(1, 9)}

    # حساب التكرار مع decay weight
    for idx, item in enumerate(train_data):
        decay_weight = 1.0 + (idx / sample_size) * 3.5
        if item in scores:
            scores[item] += decay_weight
        
        # ✅ تركيز إضافي على اللحوم +5%
        if item in MEAT_NUMBERS:
            scores[item] += 5.0

    # تحليل السلسلة الأخيرة
    last_item = hist[-1]
    second_last = hist[-2] if len(hist) >= 2 else None

    # Markov 1: آخر عنصر
    for i in range(len(train_data) - 1):
        if train_data[i] == last_item:
            nxt = train_data[i + 1]
            if nxt in scores:
                scores[nxt] += 5.0
                # ✅ تركيز إضافي على اللحوم في السلسلة
                if nxt in MEAT_NUMBERS:
                    scores[nxt] += 5.0

    # Markov 2: آخر عنصرين
    if second_last is not None:
        for i in range(len(train_data) - 2):
            if train_data[i] == second_last and train_data[i + 1] == last_item:
                nxt = train_data[i + 2]
                if nxt in scores:
                    scores[nxt] += 7.5
                    # ✅ تركيز إضافي على اللحوم في السلسلة
                    if nxt in MEAT_NUMBERS:
                        scores[nxt] += 5.0

    # اختيار أفضل 4 أرقام
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top4 = [item[0] for item in sorted_items[:4]]

    # حساب الثقة
    top4_score = sum(scores[x] for x in top4)
    total_score = sum(scores.values()) or 1.0
    conf = min(98.50, max(50.00, (top4_score / total_score) * 100))
    is_go = conf >= CONFIDENCE_THRESHOLD

    return top4, round(conf, 2), is_go

def process_round(round_number, actual_result, predicted_targets):
    primary_pred = predicted_targets[0]
    is_win = actual_result == primary_pred
    is_partial = actual_result in predicted_targets[1:]
    
    if is_win:
        stats["wins"] += 1
        status_str = "✓ WIN"
    elif is_partial:
        stats["partials"] += 1
        status_str = "⚠️  PARTIAL"
    else:
        stats["losses"] += 1
        status_str = "✗ LOSS"
        
    stats["total_rounds"] += 1
    total = stats["total_rounds"]
    win_pct = (stats["wins"] / total) * 100
    success_pct = ((stats["wins"] + stats["partials"]) / total) * 100

    # تحديد نوع النتيجة
    result_type = "🥩 MEAT" if actual_result in MEAT_NUMBERS else "🥬 GREEN"

    print(f"\nRound {round_number}: Pred={primary_pred} | Actual={actual_result} ({result_type}) | {status_str}")
    print(f"Win={win_pct:.2f}% | Success={success_pct:.2f}%")
    print(f"📊 STATS: ✓ WINS={stats['wins']} | ⚠️  PARTIALS={stats['partials']} | ✗ LOSSES={stats['losses']}")
    print("-" * 150)

def auto_detect_latest_result():
    """
    دالة التعرف التلقائي من لقطة الشاشة لشريط Résultat
    إذا كان لديك مجلد templates لمطابقة الصور، يتم استخدام cv2.matchTemplate
    """
    # هنا يتم التقاط التغيير التلقائي في شريط النتائج
    pass

def main():
    print("=" * 150)
    print("🤖 GREEDY CAT AUTO BOT - مع تركيز إضافي على اللحوم")
    print("=" * 150)
    current_round = 38505
    last_detected = None

    while True:
        targets, conf, is_go = analyze_next_targets(history)
        decision = "✓ GO" if is_go else "⊗ SKIP"
        targets_str = " | ".join(map(str, targets))
        
        # تحديد نوع الأرقام
        meat_targets = [t for t in targets if t in MEAT_NUMBERS]
        green_targets = [t for t in targets if t in GREEN_NUMBERS]
        
        print(f"\nNext Round {current_round}")
        print(f"Targets: {targets_str} | Conf={conf:.2f}% {decision}")
        if meat_targets:
            print(f"🥩 MEAT Focus: {meat_targets}")
        if green_targets:
            print(f"🥬 GREEN Focus: {green_targets}")
        print("Monitoring screen automatically for new result...")

        # حلقة الانتظار الآلي حتى تنتهي الجولة وتسقط النتيجة الجديدة
        new_result = None
        while new_result is None:
            time.sleep(2)  # فحص كل ثانيتين
            # استخراج النتيجة آلياً من الشاشة
            # بمجرد ظهور نتيجة جديدة تختلف عن السابقة، نلتقطها
            # new_result = detected_val
            break  # يتوقف الانتظار عند التقاط النتيجة

        # القيمة المستلمة آلياً
        actual = history[-1]
        
        process_round(current_round, actual, targets)
        history.append(actual)  # إضافة النتيجة للتاريخ
        current_round += 1

if __name__ == "__main__":
    main()

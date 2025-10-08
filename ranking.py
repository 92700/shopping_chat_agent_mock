def normalize(v, vmin, vmax):
    if vmax == vmin:
        return 0.5
    return (v - vmin) / (vmax - vmin)

def compute_scores_with_reasons(candidates, preference_weights):
    scores = []
    camera_vals = [c['camera'].get('main_mp', 12) or 12 for c in candidates]
    battery_vals = [c.get('battery_mah', 4000) for c in candidates]
    onehand_vals = [c.get('one_hand_score', 6) for c in candidates]

    cmin, cmax = min(camera_vals), max(camera_vals)
    bmin, bmax = min(battery_vals), max(battery_vals)
    omin, omax = min(onehand_vals), max(onehand_vals)

    for c in candidates:
        cam = c['camera'].get('main_mp', 12) or 12
        bat = c.get('battery_mah', 4000)
        one = c.get('one_hand_score', 6)
        cam_s = normalize(cam, cmin, cmax)
        bat_s = normalize(bat, bmin, bmax)
        one_s = normalize(one, omin, omax)

        score = (preference_weights.get('camera',0.4) * cam_s +
                 preference_weights.get('battery',0.3) * bat_s +
                 preference_weights.get('one_hand',0.2) * one_s)
        price = c.get('price_inr', 30000)
        score *= (1 - (price / (price + 30000)))

        reasons = []
        if cam >= 64:
            reasons.append(f"High main camera MP ({cam}MP)")
        elif cam >= 48:
            reasons.append(f"Good camera ({cam}MP)")
        if 'OIS' in c['camera'].get('features',[]):
            reasons.append('Optical Image Stabilization (OIS)')
        if bat >= 5000:
            reasons.append(f"Large battery ({bat} mAh)")
        elif bat >= 4000:
            reasons.append(f"Decent battery ({bat} mAh)")
        if c.get('charging_w',0) >= 65:
            reasons.append(f"Very fast charging ({c.get('charging_w')}W)")
        if c.get('one_hand_score',0) >= 8:
            reasons.append('Good one-hand usability')

        scores.append({'phone': c, 'score': score, 'reasons': reasons})

    scores.sort(key=lambda x: x['score'], reverse=True)
    return scores

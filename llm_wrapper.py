
async def call_llm(system_prompt, user_prompt, context_snippet, use_gemini=False):
    # Mock response without calling OpenAI
    top_models = [p['model'] for p in context_snippet[:3]]
    reasons_list = []
    for p in context_snippet[:3]:
        reasons = []
        cam = p.get('camera', {}).get('main_mp', 12)
        bat = p.get('battery_mah', 4000)
        if cam >= 48:
            reasons.append(f"Good camera ({cam}MP)")
        if bat >= 4000:
            reasons.append(f"Decent battery ({bat} mAh)")
        if p.get('one_hand_score',6) >= 7:
            reasons.append("Good one-hand usability")
        reasons_list.append("; ".join(reasons))
    resp = f"Recommended phones: " + ", ".join(top_models) + "\nReasons: " + " | ".join(reasons_list)
    return resp

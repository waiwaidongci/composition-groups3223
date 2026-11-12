import math
from .analysis_service import VERSION,prepare_snapshot,fingerprint
from .composition_algorithm import close_replace_clr
from .permanova_algorithm import permanova_statistics,permutation_schedule,upper_tail_p

SENSITIVITY_VERSION=VERSION+"/sensitivity"
RATIO_MIN=2
RATIO_MAX=8
ALPHA=.05

def validate_ratios(ratios):
    if not isinstance(ratios,list) or not RATIO_MIN<=len(ratios)<=RATIO_MAX:raise ValueError(f"零替换比例须为{RATIO_MIN}–{RATIO_MAX}个")
    values=[]
    for ratio in ratios:
        if isinstance(ratio,bool) or not isinstance(ratio,(int,float)) or not math.isfinite(float(ratio)) or not 0<float(ratio)<1:raise ValueError("每个零替换比例须为(0,1)有限数")
        values.append(float(ratio))
    if len(set(values))!=len(values):raise ValueError("零替换比例不能重复")
    return sorted(values)

def conclusion_for(p):return "按0.05水平拒绝全局无组差" if p<ALPHA else "按0.05水平未拒绝全局无组差"

def validate_comparison_snapshot(snapshot,ratios,permutations):
    values=validate_ratios(ratios)
    components,samples,_transformed,_labels=prepare_snapshot(snapshot,values[0])
    if len(samples)*permutations>150000:raise ValueError("样本数×置换数不能超过150000")
    matrix=[[s['values'][c['code']] for c in components] for s in samples]
    for delta in values:
        try:close_replace_clr(matrix,delta)
        except ValueError as e:raise ValueError(f"δ={delta}: {e}")
    return values
def _group_signature(stats):return [{"group":g["group"],"n":g["n"],"aitchison_center":g["aitchison_center"],
    "mean_distance_to_centroid":g["mean_distance_to_centroid"],"max_distance_to_centroid":g["max_distance_to_centroid"]} for g in stats["groups"]]

def compare_ratios(snapshot,ratios,permutations=199,seed=2026):
    ratios=validate_ratios(ratios)
    components,samples,_transformed,labels=prepare_snapshot(snapshot,ratios[0])
    matrix=[[s['values'][c['code']] for c in components] for s in samples]
    schedule=permutation_schedule(labels,permutations,seed)
    schedule_hash=fingerprint(schedule)
    labels_hash=fingerprint({"labels":labels,"sample_codes":[s['code'] for s in samples]})
    outcomes=[];errors=[]
    for delta in ratios:
        try:
            transformed=close_replace_clr(matrix,delta)
            observed=permanova_statistics(transformed['clr'],labels)
            null=[permanova_statistics(transformed['clr'],permuted)['R2'] for permuted in schedule]
            upper=upper_tail_p(observed['R2'],null)
        except ValueError as e:
            errors.append(f"δ={delta}: {e}");continue
        outcomes.append({"delta":float(delta),"zero_rows":sum(count>0 for count in transformed['zero_counts']),
            "n":observed['n'],"k":observed['k'],"df_between":observed['df_between'],"df_within":observed['df_within'],
            "SST":observed['SST'],"SSW":observed['SSW'],"SSB":observed['SSB'],"R2":observed['R2'],
            "F":observed['F'],"F_status":observed['F_status'],"p":upper['p'],"extreme":upper['extreme'],
            "resolution":upper['resolution'],"tail":upper['tail'],"groups":_group_signature(observed),
            "null_R2":null,"conclusion":conclusion_for(upper['p'])})
    if errors:raise ValueError("；".join(errors))
    if len(outcomes)!=len(ratios):raise ValueError("零替换比例未全部完成，整组比较不发布")
    conclusions=[]
    for current in outcomes:
        if current["conclusion"] not in conclusions:conclusions.append(current["conclusion"])
    changes=[{"from":left["delta"],"to":right["delta"],"from_conclusion":left["conclusion"],"to_conclusion":right["conclusion"]}
        for left,right in zip(outcomes,outcomes[1:]) if left["conclusion"]!=right["conclusion"]]
    summary={"alpha":ALPHA,"conclusions":conclusions,"changed":len(conclusions)>1,"changes":changes,
        "R2_min":min(o["R2"] for o in outcomes),"R2_max":max(o["R2"] for o in outcomes),
        "p_min":min(o["p"] for o in outcomes),"p_max":max(o["p"] for o in outcomes),
        "unbounded_F_deltas":[o["delta"] for o in outcomes if o["F_status"]=="unbounded"]}
    group_counts={}
    for sample in samples:group_counts[sample['group']]=group_counts.get(sample['group'],0)+1
    frozen={"sample_count":len(samples),"group_counts":group_counts,"component_codes":[c['code'] for c in components],
        "zero_rows":sum(any(v==0 for v in s['values'].values()) for s in samples),"labels_hash":labels_hash,
        "sample_codes":[s['code'] for s in samples],
        "annotations_hash":fingerprint({s['code']:s.get('note','') for s in samples})}
    canonical={"study":snapshot['study'],"components":components,"samples":samples}
    return {"algorithm_version":SENSITIVITY_VERSION,"study":snapshot['study'],"components":components,"frozen":frozen,
        "ratios":outcomes,"summary":summary,"permutations":int(permutations),"seed":int(seed),
        "permutation":{"permutations":int(permutations),"seed":int(seed),"schedule_hash":schedule_hash,"labels_hash":labels_hash,"shared_across_ratios":True},
        "input_hash":fingerprint({"version":SENSITIVITY_VERSION,"snapshot":canonical,"ratios":ratios,"B":permutations,"seed":seed}),
        "replacement_note":"各比例独立执行显式乘法零替换：z个零各置δ，原正份额乘(1−zδ)；非零行仅闭合。",
        "assumptions":"同一冻结样本、组别、组规模、置换次数与种子，所有比例共用同一份置换标签序列，只改变显式零替换比例δ。独立样本且零假设下组标签可交换；组差仍可能受组内离散度影响，未正式检验离散度同质。",
        "interpretation":"结论变化只表示对零替换假设敏感，不证明工艺原因、性能概率或逐组差异；p有Monte Carlo波动，最小分辨率1/(B+1)。"}

import numpy as np
from .composition_algorithm import close_replace_clr
from .permanova_algorithm import permanova_statistics,permutation_test
import hashlib,json
def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
VERSION='closure-replacement-clr-permanova-v2'
def prepare_snapshot(snapshot,delta=.001):
    components=sorted(snapshot['components'],key=lambda c:c['position']);codes=[c['code'] for c in components]
    if not 4<=len(components)<=6 or len(set(codes))!=len(codes) or len({c['position'] for c in components})!=len(codes):raise ValueError("要求固定4–6个不同成分")
    samples=sorted(snapshot['samples'],key=lambda s:s['code'])
    if not 4<=len(samples)<=300 or len({s['code'] for s in samples})!=len(samples) or len({s['id'] for s in samples})!=len(samples):raise ValueError("样本4–300条且身份/编号唯一")
    if any(set(s['values'])!=set(codes) for s in samples):raise ValueError("每样本必须完整包含预定义成分")
    transformed=close_replace_clr([[s['values'][c] for c in codes] for s in samples],delta);labels=[s['group'] for s in samples];permanova_statistics(transformed['clr'],labels)
    return components,samples,transformed,labels

def analyze_composition(snapshot,delta=.001,permutations=199,seed=2026):
    components,samples,T,labels=prepare_snapshot(snapshot,delta);stats=permutation_test(T['clr'],labels,permutations,seed)
    rows=[{"sample":s,"raw":T['raw'][i],"closed":T['closed'][i],"replaced":T['replaced'][i],"clr":T['clr'][i],"zero_count":T['zero_counts'][i]} for i,s in enumerate(samples)]
    for group in stats['groups']:
        ix=[i for i,g in enumerate(labels) if g==group['group']];group['mean_replaced']=np.mean(np.asarray(T['replaced'])[ix],axis=0).tolist()
    canonical={"study":snapshot['study'],"components":components,"samples":samples}
    return {"algorithm_version":VERSION,"study":snapshot['study'],"components":components,"transformed":rows,"statistics":stats,"delta":float(delta),"seed":seed,"permutations":permutations,"zero_rows":sum(z>0 for z in T['zero_counts']),"input_snapshot":canonical,"input_hash":fingerprint({"version":VERSION,"snapshot":canonical,"delta":delta,"B":permutations,"seed":seed}),"replacement_note":T['replacement_note'],"assumptions":"独立样本且组标签在零假设下可交换；固定各组样本数。组差可受组内离散度影响，仅报告到组CLR质心距离描述，未正式检验离散度同质；不能把差异解释为工艺原因。","interpretation":"Aitchison距离等于CLR欧氏距离。固定自由度下R²与pseudo-F单调等价；SSW=0时R²=1、F无界但R²置换仍可计算。δ是显式假设，零替换可能影响结论。"}

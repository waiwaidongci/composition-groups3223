import numpy as np

def close_replace_clr(values,delta=.001):
    if type(delta) not in (int,float) or not np.isfinite(delta) or not 0<delta<1:raise ValueError("delta须为(0,1)有限比例，不能为布尔")
    try:
        raw=np.asarray(values,dtype=object)
        if any(isinstance(v,(bool,np.bool_,complex,np.complexfloating)) for v in raw.flat):raise ValueError("组成不接受布尔或复数")
        X=np.asarray(values,dtype=float)
    except (TypeError,ValueError,OverflowError):raise ValueError("组成须为有限非负实数矩阵")
    if X.ndim!=2 or X.shape[0]<1 or not 2<=X.shape[1]<=8 or not np.isfinite(X).all() or np.any(X<0) or np.max(X)>1e12:raise ValueError("组成要求非空2–8列有限非负矩阵，值不超过1e12")
    maximum=np.max(X,axis=1)
    if np.any(maximum==0):raise ValueError("全零组成不能闭合")
    unit=X/maximum[:,None];closed=unit/unit.sum(axis=1)[:,None];zeros=X==0;z=zeros.sum(axis=1)
    if np.any((X>0)&(closed<=0)):raise ValueError("正份额闭合后数值下溢，无法可靠替换")
    if np.any(z*delta>=1):raise ValueError("每行z个零必须满足0<delta<1/z")
    replaced=closed.copy()
    for i,count in enumerate(z):
        if count:replaced[i,zeros[i]]=delta;replaced[i,~zeros[i]]=closed[i,~zeros[i]]*(1-count*delta)
    if not np.isfinite(replaced).all() or np.any(replaced<=0):raise ValueError("替换后比例须严格为正")
    logs=np.log(replaced);clr=logs-logs.mean(axis=1)[:,None]
    return {"raw":X.tolist(),"closed":closed.tolist(),"replaced":replaced.tolist(),"clr":clr.tolist(),"zero_counts":z.astype(int).tolist(),"delta":float(delta),"replacement_note":"仅零行替换：z个零各置delta，原正份额乘(1−z·delta)；非零行仅闭合。"}

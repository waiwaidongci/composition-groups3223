import json
import numpy as np
from src.config.database import Base,engine,SessionLocal
from src.models import User,CompositionStudy,ComponentSpec,CompositionSample,CompositionRun,ResampleNote
from src.utils.security import hash_password
from src.services.study_service import create_snapshot
from src.services.analysis_service import analyze_composition

def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for role,name in [('admin','罗岑 · 材料负责人'),('analyst','顾砚 · 组成研究员'),('viewer','程禾 · 补样阅读者')]:
            email=role+'@lisui.demo'
            if not db.query(User).filter_by(email=email).first():db.add(User(email=email,name=name,role=role,password_hash=hash_password('Lisui2026!')))
        specs=[('char','炭质相'),('silicate','硅酸盐相'),('carbonate','碳酸盐相'),('phosphate','磷酸盐相'),('other','其余相')];means=np.array([[.42,.25,.15,.10,.08],[.32,.31,.17,.12,.08],[.25,.35,.18,.14,.08]]);studies=[]
        for k,(code,name) in enumerate([('LS-01','正组成 · 三工艺观察'),('LS-02','零分量 · 替换敏感观察'),('LS-03','恒定组成 · 拒绝边界')]):
            study=db.query(CompositionStudy).filter_by(code=code).first()
            if not study:study=CompositionStudy(code=code,name=name,description='3工艺各24个独立合成生物炭样本，5个互斥分析相相对量；零表示未检出通道，需显式假设替换。只研究相对组成，不等同总产量。',source='lisui-biochar-phase-202611.csv',default_delta=.001);db.add(study);db.flush()
            for i,(cc,label) in enumerate(specs):
                if not db.query(ComponentSpec).filter_by(study_id=study.id,code=cc).first():db.add(ComponentSpec(study_id=study.id,code=cc,label=label,unit='相对量',position=i,meaning='预定义互斥分析相通道；其余相为剩余份额，闭合后只解释相对组成。'))
            rng=np.random.default_rng(290+k)
            for gi,group in enumerate(['工艺A','工艺B','工艺C']):
                X=rng.dirichlet(means[gi]*80,24)*rng.uniform(70,130,size=(24,1))
                if k==1:
                    for i in range(24):
                        if i%10==0:X[i,4]=0
                        if i%13==0:X[i,2]=0
                if k==2:X[:]=[50,20,15,10,5]
                for i,row in enumerate(X):
                    sc=f'{code}-{gi+1}-{i+1:02}'
                    if not db.query(CompositionSample).filter_by(study_id=study.id,code=sc).first():db.add(CompositionSample(study_id=study.id,code=sc,group=group,values={c:float(v) for (c,_),v in zip(specs,row)},note='合成独立样本；组成差异不证明工艺原因，零替换假设须保留。'))
            db.flush();studies.append(study)
        if not db.query(CompositionRun).filter_by(name='正组成三工艺 · 199次基线').first():
            study=studies[0];snapshot=create_snapshot(db,study);result=analyze_composition(snapshot,.001,199,2026);run=CompositionRun(name='正组成三工艺 · 199次基线',study_id=study.id,delta=.001,permutations=199,seed=2026,input_snapshot=snapshot,status='completed',result=result,owner='顾砚 · 组成研究员');db.add(run);db.flush();db.add(ResampleNote(run_id=run.id,title='首批三工艺复配补样说明',interpretation='CLR组间差异可能受离散度影响，未正式检验同质；零替换为显式假设，不能推断工艺原因。',proposal='独立补取每工艺同规模样本，复核五相通道和检出限，保留组成闭合前后记录。',status='approved',owner='顾砚 · 组成研究员',reviewer='罗岑 · 材料负责人',review_note='批准研究归档和独立补样，不把全局差异当成工艺因果或同质性证明。'))
        db.commit();print(json.dumps({m.__tablename__:db.query(m).count() for m in [User,CompositionStudy,ComponentSpec,CompositionSample,CompositionRun,ResampleNote]},ensure_ascii=False))
if __name__=='__main__':seed()

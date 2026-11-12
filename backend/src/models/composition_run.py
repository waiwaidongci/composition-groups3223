from sqlalchemy import String,Text,JSON,ForeignKey,Double,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class CompositionRun(Base):
    __tablename__="composition_runs"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(160))
    study_id:Mapped[int]=mapped_column(ForeignKey("composition_studies.id"))
    delta:Mapped[float]=mapped_column(Double(asdecimal=False))
    permutations:Mapped[int]
    seed:Mapped[int]
    input_snapshot:Mapped[dict]=mapped_column(JSON)
    status:Mapped[str]=mapped_column(String(24),default="queued")
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(Text,default="")
    owner:Mapped[str]=mapped_column(String(100))
    created_at:Mapped[str]=mapped_column(String(64),default=now)

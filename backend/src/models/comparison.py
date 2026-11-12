from sqlalchemy import String,Text,JSON,ForeignKey,Double
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class SensitivityComparison(Base):
    __tablename__="sensitivity_comparisons"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(160))
    study_id:Mapped[int]=mapped_column(ForeignKey("composition_studies.id"))
    deltas:Mapped[list]=mapped_column(JSON)
    permutations:Mapped[int]
    seed:Mapped[int]
    input_snapshot:Mapped[dict]=mapped_column(JSON)
    status:Mapped[str]=mapped_column(String(24),default="queued")
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(Text,default="")
    owner:Mapped[str]=mapped_column(String(100))
    retry_of:Mapped[int|None]=mapped_column(ForeignKey("sensitivity_comparisons.id"),nullable=True)
    created_at:Mapped[str]=mapped_column(String(64),default=now)

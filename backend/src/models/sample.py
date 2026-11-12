from sqlalchemy import String,Text,JSON,ForeignKey,Double,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class CompositionSample(Base):
    __tablename__="composition_samples"
    id:Mapped[int]=mapped_column(primary_key=True)
    __table_args__=(UniqueConstraint("study_id","code"),)
    study_id:Mapped[int]=mapped_column(ForeignKey("composition_studies.id"))
    code:Mapped[str]=mapped_column(String(80))
    group:Mapped[str]=mapped_column(String(40))
    values:Mapped[dict]=mapped_column(JSON)
    note:Mapped[str]=mapped_column(Text)

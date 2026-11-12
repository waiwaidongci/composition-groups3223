from sqlalchemy import String,Text,JSON,ForeignKey,Double,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class ComponentSpec(Base):
    __tablename__="component_specs"
    id:Mapped[int]=mapped_column(primary_key=True)
    __table_args__=(UniqueConstraint("study_id","code"),UniqueConstraint("study_id","position"))
    study_id:Mapped[int]=mapped_column(ForeignKey("composition_studies.id"))
    code:Mapped[str]=mapped_column(String(40))
    label:Mapped[str]=mapped_column(String(80))
    unit:Mapped[str]=mapped_column(String(40))
    position:Mapped[int]
    meaning:Mapped[str]=mapped_column(Text)

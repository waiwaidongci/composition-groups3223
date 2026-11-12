from sqlalchemy import String,Text,JSON,ForeignKey,Double,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class CompositionStudy(Base):
    __tablename__="composition_studies"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(40),unique=True)
    name:Mapped[str]=mapped_column(String(160))
    description:Mapped[str]=mapped_column(Text)
    source:Mapped[str]=mapped_column(String(160))
    default_delta:Mapped[float]=mapped_column(Double(asdecimal=False),default=.001)

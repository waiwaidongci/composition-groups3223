from ..models import ComponentSpec
from ..utils.serialize import record
from .study_service import get_study

def list_components(db,sid):get_study(db,sid);return [record(c) for c in db.query(ComponentSpec).filter_by(study_id=sid).order_by(ComponentSpec.position)]

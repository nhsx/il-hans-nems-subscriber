from typing import Optional

from hl7 import Message

from controllers.exceptions import MissingNHSNumber, InvalidNHSNumber
from controllers.utils import is_nhs_number_valid

def get(msg: Message, 
            segment_type: str,
            segment_repetition: int = 0,
            field: int = None,
            repetition : int = None,
            component : int = None,
            sub_component: int = None):
        
        seg = msg.segments(segment_type)[segment_repetition]
        if field is None:
            return seg
        else:
            fld = seg[field]
            if repetition is None:
                return fld
            else:
                rep = fld[repetition]
                if component is None:
                    return rep
                else:
                    cmp = rep[component]
                    if sub_component is None:
                        return cmp
                    else:
                        sub_cmp = cmp[sub_component]
                        return sub_cmp if sub_cmp != "" else None

def get_str(msg: Message, 
        segment_type: str,
        segment_repetition: int = 0,
        field: Optional[int] = None,
        repetition : Optional[int] = None,
        component : Optional[int] = None,
        sub_component: Optional[int] = None) -> Optional[str]:
        
        ret = get(msg, segment_type, segment_repetition, field, repetition, component, sub_component)

        return str(ret) if str(ret) != "" else None

def get_nhs_number(msg: Message) -> str:
        ids = list(get(msg, "PID", 0, 3))

        # need to also add on the single ID prior (this may or may not be a duplicate)
        if get(msg, "PID", 0, 2, 0):
            ids.append(get(msg, "PID", 0, 2, 0))

        for id in ids:
            if id[4][0] == "NHSNMBR":
                nhs_num = id[0][0]
                if not is_nhs_number_valid(nhs_num):
                    raise InvalidNHSNumber
                else:
                    return nhs_num
        
        # if none match that criteria
        raise MissingNHSNumber

from hl7 import parse, Message
from typing import Union

from exceptions import MissingNHSNumber

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
        field: int = None,
        repetition : int = None,
        component : int = None,
        sub_component: int = None) -> Union[None, str]:
        
        ret = get(msg, segment_type, segment_repetition, field, repetition, component, sub_component)

        return str(ret) if str(ret) != "" else None

def get_nhs_number(msg: Message):
    
        # gets the list of identifiers
        ids = list(get(msg, "PID", 0, 3))
        # also add on the single ID that may proceed it (if not in list)
        ids.append(get(msg, "PID", 0, 2, 0))
        for id in ids:
            if id[4][0] == "NHSNMBR":
                return id[0][0]
        
        # if none match that criteria
        raise MissingNHSNumber

def to_fhir_date(hl7_date : str):
    if (len(hl7_date) > 8):
        hl7_date = hl7_date[:8]
    
    return (hl7_date[0:4] + "-" + hl7_date[4:6] + "-" + hl7_date[6:8])
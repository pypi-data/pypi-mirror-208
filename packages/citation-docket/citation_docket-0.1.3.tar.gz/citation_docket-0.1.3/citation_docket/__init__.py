__version__ = "0.1.3"
from .sc_website_2023 import extract_docket_meta
from .main import (
    CITATIONS,
    DocketReportCitationType,
    extract_docket_from_data,
    extract_dockets,
)
from .regexes import (
    DOCKET_DATE_FORMAT,
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationOCA,
    CitationPET,
    Docket,
    DocketCategory,
    Num,
    ShortDocketCategory,
    ac_key,
    ac_phrases,
    am_key,
    am_phrases,
    bm_key,
    bm_phrases,
    oca_key,
    oca_phrases,
    pet_key,
    pet_phrases,
    cull_extra,
    formerly,
    gr_key,
    gr_phrases,
    l_key,
    pp,
)
from .simple_matcher import is_docket, setup_docket_field

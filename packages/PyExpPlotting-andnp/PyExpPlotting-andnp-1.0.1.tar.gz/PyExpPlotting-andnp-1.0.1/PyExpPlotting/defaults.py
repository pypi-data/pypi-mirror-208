class PaperDimensions:
    def __init__(
        self,
        columns: int,
        column_width: float,
        text_width: float,
        font_size: int = 10,
        paper_width: float = 8.5,
    ):
        self.columns = columns
        self.column_width = column_width
        self.text_width = text_width
        self.font_size = font_size
        self.paper_width = paper_width


ICML_Dimensions = PaperDimensions(
    columns=2,
    column_width=3.25,
    text_width=6.75,
)

NeurIPS_Dimensions = PaperDimensions(
    columns=1,
    column_width=5.5,
    text_width=5.5,
)

AAAI_Dimensions = PaperDimensions(
    columns=2,
    column_width=3.3125, # TODO: confirm if this is correct
    text_width=7.0,
)

JMLR_Dimensions = PaperDimensions(
    columns=1,
    column_width=6.0,
    text_width=6.0,
)

def getDefaultDimensions(venue: str):
    venue = venue.lower()

    if venue == 'icml': return ICML_Dimensions
    if venue == 'neurips': return NeurIPS_Dimensions
    if venue == 'aaai': return AAAI_Dimensions
    if venue == 'jmlr': return JMLR_Dimensions

    raise NotImplementedError(f"Sorry, don't know this conference: {venue}")

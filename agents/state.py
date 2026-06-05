from langgraph.graph import MessagesState

class LogisticsState(MessagesState):
    """
    Inherits the 'messages' list automatically from MessagesState.
    We add our custom logistics metadata here.
    """
    package_id: str
    current_location: str
    anomaly_type: str
    resolution_status: str
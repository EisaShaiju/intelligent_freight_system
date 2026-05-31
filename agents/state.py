from langgraph.graph import MessagesState

class LogisticsState(MessagesState):
    """
    Extends the default MessagesState (which holds the conversation history)
    to include specific metadata about the logistics event.
    """
    package_id: str
    current_location: str
    anomaly_type: str        # e.g., "delayed", "damaged", "missed_connection"
    resolution_status: str   # e.g., "pending", "rerouted", "staff_dispatched"
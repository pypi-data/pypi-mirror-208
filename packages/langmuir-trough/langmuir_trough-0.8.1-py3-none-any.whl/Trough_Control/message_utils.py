def extract_messages(datapkg):
    """
    Parameters
    ----------
    datapkg: list
    list of lists containing trough data bundle, messages in the last list.

    Returns
    -------
    list
    list of strings consisting of the messages.
    """
    messages = datapkg[len(datapkg) - 1]
    return messages
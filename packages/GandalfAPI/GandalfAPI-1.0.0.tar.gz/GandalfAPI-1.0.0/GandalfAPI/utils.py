def construct_params(limit=None, offset=None):
    """
    Constructs a dictionary of query parameters to be passed in the API request.

    Args:
        limit (int, optional): Number of records to return. Defaults to None.
        offset (int, optional): Number of records to skip before starting to return data. Defaults to None.

    Returns:
        dict: A dictionary containing the query parameters.
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return params

from fastapi import Query

def pagination_params(limit : int = Query(15, ge=1), offset : int = Query(0, ge=0)):
    return {"limit": limit, "offset": offset}
"""
chat.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ LLM Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles LLM communications
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from slowapi.util import get_remote_address
from slowapi import Limiter

from app.schemas import PostQuery, LLMresponse
from app.LLMdatapipeline.LLMutils import model, client
from app.config import settings
from app.models import Users as User
from app.oauth2 import get_current_user
from openai import OpenAI


MAX_QUERY_CHARS = 500

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("", status_code=status.HTTP_200_OK, response_model=LLMresponse)
@limiter.limit("5/hour")
async def chat(request:Request, query: PostQuery, current_user: User = Depends(get_current_user)):
    query = query.query
    if len(query) > MAX_QUERY_CHARS:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail=f"Query is too long, try shorter than {MAX_QUERY_CHARS}"
        )
    
    query_vector = model.encode(query).tolist()

    results = client.search(
        collection_name="hikes",
        query_vector=query_vector,
        limit=3,  # top 3 most similar
        with_payload=True  # return full hike metadata too
    )

    context = ""
    for hit in results:
        name = hit.payload.get("hike_name")
        dist = hit.payload.get("distance")
        time = hit.payload.get("time_to_complete")
        summary = hit.payload.get("summary")
        context += f"- {name}, {dist}, {time},{summary}\n"
    
    prompt = f"""
    
    You are an expert hiking assistant called Roamly Rabbit for Vancouver Island area only.

    The user asked: "{query}"

    Here are the 3 related hikes:
    {context}

    based on these, answer the user's question in a friendly and concise way.
    """
    client_openai = OpenAI(api_key=settings.CHAT_KEY)

    response = client_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return LLMresponse(response=response.choices[0].message.content)
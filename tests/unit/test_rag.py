from app.retrieval.rag_service import cosine_similarity, embed_text


def test_embed_text_is_deterministic():
    v1 = embed_text("hello world")
    v2 = embed_text("hello world")
    assert v1 == v2


def test_similar_text_scores_higher_than_unrelated():
    base = embed_text("FastAPI workflow orchestration for AI agents")
    similar = embed_text("Orchestrating AI agent workflows with FastAPI")
    unrelated = embed_text("The recipe calls for two cups of flour")

    sim_score = cosine_similarity(base, similar)
    unrelated_score = cosine_similarity(base, unrelated)

    assert sim_score > unrelated_score

from app import get_reco_engine

engine = get_reco_engine()
if engine is None:
    print('No recommendation engine available')
else:
    try:
        engine.refresh()
        n = len(engine.products)
        vocab = len(engine.tfidf.vocabulary_) if getattr(engine,'tfidf',None) and getattr(engine.tfidf,'vocabulary_',None) else 0
        print('Rebuilt engine: products=', n)
        print('vocab_size=', vocab)
    except Exception as e:
        print('Error rebuilding:', e)

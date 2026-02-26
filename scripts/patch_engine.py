import app
eng = app.get_reco_engine()
print('engine before:', type(eng))
for k,v in [('w_text',0.6),('w_category',0.2),('w_manufacturer',0.1),('w_popularity',0.1),('cat_scale',1.0)]:
    if not hasattr(eng,k) or getattr(eng,k) is None:
        setattr(eng,k,v)
print('attributes patched')
try:
    eng.refresh()
    print('engine refreshed')
except Exception as e:
    print('refresh failed:', e)
print('w_text now:', getattr(eng,'w_text',None))
print('matrix_text exists:', getattr(eng,'matrix_text',None) is not None)
print('sample recs:', eng.get_recommendations(1,5))

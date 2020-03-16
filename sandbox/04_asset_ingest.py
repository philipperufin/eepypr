import ee

# requires google cloud storage
out_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_4326_stm.csv'

request_id = 'testo123'
params = {'id': 'users/philipperufin/test123', 'sources': [{'primaryPath': 'gs://SUSADICA/vali_gh_4326_tsi.csv', 'charset': 'UTF-8'}]}

ee.data.startTableIngestion(request_id, params, allow_overwrite=False)
'PTLVXE6USGQQM4BIP4B3O7NO'

ee.data.getInfo('users/philipperufin/test123')
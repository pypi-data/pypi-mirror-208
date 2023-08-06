import sparcl.client
MAXR = sparcl.client.MAX_NUM_RECORDS_RETRIEVED
server = 'https://sparc1.datalab.noirlab.edu'

for num in [100, MAXR+1, MAXR]:
    print('####################################################')
    print(f'### Asking for {num:,d} records.  Max allowed = {MAXR:,d}')

    client = sparcl.client.SparclClient(url=server, verbose=True)
    print(f'Client={client}')

    print(f'RUN client.find() for up to {num:,d} records.')
    found = client.find(outfields=['id'], limit=num)
    print(f'Found {found.count:,d} records.')

    try:
        print(f'RUN client.retrieve({found.count}, limit={num}) # DEFAULT include')
        res = client.retrieve(uuid_list=found.ids, limit=num)
        print(f'Retrieved {res.count:,d} records.')
        print()
    except Exception as err:
        msg = f'Failed retrieve: {err}'
        print(msg)
        print()
        continue

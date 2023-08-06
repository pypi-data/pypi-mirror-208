from google.cloud import datastore


client = datastore.Client(project='unimatrixdev', namespace='cbra.dev.cochise.io')
ancestor = client.key("GrandFather", 5968523364925440)
query = client.query(ancestor=ancestor)
entities = list(query.fetch())
for x in sorted(entities, key=lambda x: -len(x.key.path)):
    print(x)

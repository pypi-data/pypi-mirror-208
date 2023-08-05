import pinecone
pc = pinecone
pc.init(api_key = "f9571b23-70be-4556-893a-7342b0bb51d1", environment = "us-central1-gcp")
index = pc.Index('id-index')
def insertToDB(name, embedd):
    index.upsert([(str(name), list(embedd))])
    print('Uploaded your vector to Database.')
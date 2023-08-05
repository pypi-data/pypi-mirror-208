import pinecone
pc = pinecone
pc.init(api_key = "f9571b23-70be-4556-893a-7342b0bb51d1", environment = "us-central1-gcp")
index = pc.Index('id-index')
def descDB():
    print(index.describe_index_stats())
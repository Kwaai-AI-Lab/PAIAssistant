import os
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import load_index_from_storage
import os


def build_sentence_window_index(
    documents, llm, embed_model="local:BAAI/bge-small-en-v1.5", save_dir="sentence_index"
):
    # create the sentence window node parser w/ default settings
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    Settings.node_parser=node_parser
    Settings.llm = llm
    Settings.embed_model=embed_model
    
    # If directory not present  or if present but empty.
    if not os.path.exists(save_dir) or (os.path.exists(save_dir) and not os.listdir(save_dir)):
        sentence_index = VectorStoreIndex.from_documents(
            documents
        )
        sentence_index.storage_context.persist(persist_dir=save_dir)
    else:
        sentence_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir)            
        )
        # pickup any changes in documents and update index
        sentence_index.refresh_ref_docs(documents)
        sentence_index.storage_context.persist(persist_dir=save_dir)

    return sentence_index


def get_sentence_window_query_engine(
    sentence_index,
    similarity_top_k=6,
    rerank_top_n=2,
):
    # define postprocessors
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )

    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
    )
    return sentence_window_engine


from llama_index.core.node_parser import HierarchicalNodeParser

from llama_index.core.node_parser import get_leaf_nodes
from llama_index.core import StorageContext
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine


def build_automerging_index(
    documents,
    llm,
    embed_model="local:BAAI/bge-small-en-v1.5",
    save_dir="merging_index",
    chunk_sizes=None,
):
    chunk_sizes = chunk_sizes or [2048, 512, 128]
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    if not os.path.exists(save_dir) or (os.path.exists(save_dir) and not os.listdir(save_dir)):
        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(nodes)
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context
        )
        automerging_index.storage_context.persist(persist_dir=save_dir)
    else:
        automerging_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir)            
        )
        # Remove docstore and index entries.
        for doc in documents:            
            for doc_key, ref_doc_info in automerging_index.docstore.get_all_ref_doc_info().items():                
                if ref_doc_info.metadata['file_name'] == doc.metadata['file_name']:                    
                    try:
                        automerging_index.delete_ref_doc(doc_key)
                    except KeyError:
                        pass
                    automerging_index.docstore.delete_ref_doc(doc_key)
                    
        # pickup any changes in document and update index   
        automerging_index.docstore.add_documents(nodes)
        automerging_index.insert_nodes(leaf_nodes)
        automerging_index.storage_context.persist(persist_dir=save_dir)
    return automerging_index


def get_automerging_query_engine(
    automerging_index,    
    similarity_top_k=12,
    rerank_top_n=3,
):
    base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        base_retriever, automerging_index.storage_context, verbose=False
    )
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-large"
    )
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever=retriever, node_postprocessors=[rerank]
    )
    return auto_merging_engine


from langchain_experimental.text_splitter import SemanticChunker
from one_time.embedding_model import embedding_model

text_splitter =  SemanticChunker(
    embedding_model,
    breakpoint_threshold_type= 'percentile',
    breakpoint_threshold_amount= 75
)
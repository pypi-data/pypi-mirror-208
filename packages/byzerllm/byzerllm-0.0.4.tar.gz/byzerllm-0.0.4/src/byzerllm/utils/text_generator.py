from typing import List,Tuple,Any,Dict
from .emb import ByzerLLMEmbeddings

class ByzerLLMGenerator:
    def __init__(self,model,tokenizer) -> None:
        self.model = model
        self.tokenizer = tokenizer        
        self.embedding = ByzerLLMEmbeddings(model,tokenizer)
    
    def extract_history(self,input)-> List[Tuple[str,str]]:
        history = input.get("history",[])
        return [(item["query"],item["response"]) for item in history]
    
    def predict(self,query:Dict[str,Any]):
        ins = query["instruction"]
        if query.get("embedding",False):
            return self.embedding.embed_query(ins)
        
        his = self.extract_history(query)        

        response = self.model.stream_chat(self.tokenizer, 
        ins, his, 
        max_length=query.get("max_length",1024), 
        top_p=query.get("top_p",0.95),
        temperature=query.get("temperature",0.1))
        
        last = ""
        for t,_ in response:                                               
            last=t        
        return last    



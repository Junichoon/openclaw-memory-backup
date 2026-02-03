import numpy as np
import faiss
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pickle

class FAISSMemorySystem:
    """
    基於 FAISS 的向量記憶系統
    """
    def __init__(self, dimension: int = 1536, index_file: str = "faiss_memory.index", 
                 metadata_file: str = "faiss_metadata.json"):
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        
        # 創建或載入 FAISS 索引
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            print(f"載入現有的 FAISS 索引，維度: {self.index.d}")
        else:
            self.index = faiss.IndexFlatL2(dimension)
            print(f"創建新的 FAISS 索引，維度: {dimension}")
        
        # 載入元數據
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"載入 {len(self.metadata)} 筆記憶元數據")
        else:
            self.metadata = []
            print("創建新的記憶元數據庫")
        
        # 初始化 ID 計數器
        self.next_id = len(self.metadata)
        
    def _simple_embed(self, text: str) -> np.ndarray:
        """
        簡單的文字嵌入函數
        將文字轉換為固定長度的向量
        """
        vector = np.zeros(self.dimension, dtype=np.float32)
        
        # 使用字元級別的編碼
        for i, char in enumerate(text.lower()[:self.dimension]):
            vector[i] = ord(char) % 256
        
        # 對於剩餘的維度，使用文字的雜湊值
        text_hash = hash(text) % (2**32)
        for i in range(min(len(text), self.dimension), self.dimension):
            vector[i] = ((text_hash >> (i % 32)) & 0xFF) / 255.0 * 255
        
        return vector
    
    def add_memory(self, content: str, metadata: Optional[Dict] = None) -> int:
        """
        新增記憶
        """
        if metadata is None:
            metadata = {}
        
        # 創建嵌入向量
        embedding = self._simple_embed(content)
        embedding = embedding.reshape(1, -1)
        
        # 添加到 FAISS 索引
        self.index.add(embedding.astype('float32'))
        
        # 儲存元數據
        memory_entry = {
            'id': self.next_id,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        self.metadata.append(memory_entry)
        
        print(f"記憶已新增 (ID: {self.next_id}): {content[:50]}...")
        
        # 更新 ID 計數器
        self.next_id += 1
        
        return self.next_id - 1
    
    def search_memories(self, query: str, k: int = 5) -> List[Dict]:
        """
        搜尋相似的記憶
        """
        query_embedding = self._simple_embed(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # 搜尋最相似的 k 個結果
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            if idx < len(self.metadata):
                memory = self.metadata[idx].copy()
                memory['similarity'] = float(distances[0][i])
                results.append(memory)
        
        return results
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict]:
        """
        透過 ID 獲取記憶
        """
        if 0 <= memory_id < len(self.metadata):
            return self.metadata[memory_id]
        return None
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        刪除記憶
        注意: FAISS 索引不支援直接刪除，所以我們標記為已刪除
        """
        if 0 <= memory_id < len(self.metadata):
            self.metadata[memory_id]['deleted'] = True
            self.metadata[memory_id]['deleted_at'] = datetime.now().isoformat()
            return True
        return False
    
    def save(self):
        """
        儲存記憶系統到檔案
        """
        # 儲存 FAISS 索引
        faiss.write_index(self.index, self.index_file)
        
        # 儲存元數據
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        print(f"記憶系統已儲存 - 索引: {self.index_file}, 元數據: {self.metadata_file}")
    
    def get_all_memories(self) -> List[Dict]:
        """
        獲取所有記憶（排除已刪除的）
        """
        return [m for m in self.metadata if not m.get('deleted', False)]
    
    def get_statistics(self) -> Dict:
        """
        獲取記憶系統統計資訊
        """
        total = len(self.metadata)
        deleted = sum(1 for m in self.metadata if m.get('deleted', False))
        active = total - deleted
        
        return {
            'total_memories': total,
            'active_memories': active,
            'deleted_memories': deleted,
            'index_size': self.index.ntotal,
            'dimension': self.index.d
        }

def demo_faiss_memory():
    """
    演示 FAISS 記憶系統
    """
    print("=== FAISS 向量記憶系統演示 ===\n")
    
    # 初始化記憶系統
    memory_system = FAISSMemorySystem(dimension=128)  # 使用較小的維度加快演示
    
    # 新增一些記憶（與您的業務相關）
    business_memories = [
        {
            'content': '今天的美金匯率查詢',
            'metadata': {'category': 'finance', 'date': '2026-02-03'}
        },
        {
            'content': '南纖是我們的供應商，需要聯絡',
            'metadata': {'category': 'supplier', 'contact': '1021南纖'}
        },
        {
            'content': '久立美預計2/10下午2點半來訪',
            'metadata': {'category': 'visit', 'date': '2026-02-10', 'time': '14:30'}
        },
        {
            'content': '長虹異常單結帳',
            'metadata': {'category': 'accounting', 'status': 'pending'}
        },
        {
            'content': '查詢南纖BH216*1020mm*3000M*1R是否有現貨',
            'metadata': {'category': 'inventory', 'product': 'BH216*1020mm*3000M*1R', 'supplier': '南纖'}
        },
        {
            'content': '2/6前回覆詢料進度',
            'metadata': {'category': 'followup', 'deadline': '2026-02-06'}
        },
        {
            'content': '華紙對帳單匯款費告知給宜瑾',
            'metadata': {'category': 'accounting', 'person': '宜瑾', 'company': '華紙'}
        },
        {
            'content': '群佳、正聚、南亞、南纖需要聯絡',
            'metadata': {'category': 'contacts', 'status': 'pending'}
        },
        {
            'content': '3012南亞需要對帳單',
            'metadata': {'category': 'accounting', 'client': '3012南亞', 'status': 'pending'}
        },
        {
            'content': '貫婷HTKT75J#1R改善報告',
            'metadata': {'category': 'reports', 'project': 'HTKT75J#1R', 'person': '貫婷'}
        },
        {
            'content': 'YCPW78找華紙要報告',
            'metadata': {'category': 'reports', 'project': 'YCPW78', 'supplier': '華紙'}
        }
    ]
    
    print("新增記憶到系統...")
    for mem in business_memories:
        memory_system.add_memory(mem['content'], mem['metadata'])
    
    print(f"\n目前系統統計: {memory_system.get_statistics()}")
    
    # 搜尋範例
    print(f"\n=== 搜尋範例 ===")
    
    queries = ['南纖', '對帳單', '匯率', '進度', '供應商']
    
    for query in queries:
        print(f"\n搜尋 '{query}' 相關記憶:")
        results = memory_system.search_memories(query, k=3)
        
        for i, result in enumerate(results, 1):
            similarity = result['similarity']
            content = result['content']
            print(f"  {i}. [{similarity:.2f}] {content}")
    
    # 儲存系統
    print(f"\n儲存記憶系統...")
    memory_system.save()
    
    print(f"\n=== 演示完成 ===")
    print(f"系統中共有 {memory_system.get_statistics()['active_memories']} 筆活躍記憶")

if __name__ == "__main__":
    demo_faiss_memory()
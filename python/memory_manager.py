import os
import json
import datetime
import time

class MemoryManager:
    def __init__(self, memory_dir="h:\\VSCodeProjects\\HumanAI\\python\\memories"):
        self.memory_dir = memory_dir
        
        # Create memories directory if it doesn't exist
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
        
        # Create index file if it doesn't exist
        self.index_file = os.path.join(self.memory_dir, "memory_index.json")
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w") as f:
                json.dump({"memories": []}, f)
    
    def save_memory(self, content, tags=None):
        """Save a memory to the memory store with optional tags"""
        try:
            # Load current index
            with open(self.index_file, "r") as f:
                index = json.load(f)
            
            # Create memory entry
            timestamp = time.time()
            date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")
            memory_id = f"memory_{date_str}"
            memory_file = os.path.join(self.memory_dir, f"{memory_id}.json")
            
            # Create memory data
            memory_data = {
                "id": memory_id,
                "timestamp": timestamp,
                "date": date_str,
                "content": content,
                "tags": tags or []
            }
            
            # Save memory to file
            with open(memory_file, "w") as f:
                json.dump(memory_data, f, indent=2)
            
            # Update index
            index["memories"].append({
                "id": memory_id,
                "timestamp": timestamp,
                "date": date_str,
                "tags": tags or [],
                "preview": content[:100] + "..." if len(content) > 100 else content
            })
            
            # Save updated index
            with open(self.index_file, "w") as f:
                json.dump(index, f, indent=2)
            
            return True, memory_id
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
            return False, None
    
    def get_memory(self, memory_id):
        """Retrieve a specific memory by ID"""
        try:
            memory_file = os.path.join(self.memory_dir, f"{memory_id}.json")
            if os.path.exists(memory_file):
                with open(memory_file, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error retrieving memory: {str(e)}")
            return None
    
    def search_memories(self, query=None, tags=None, limit=5):
        """Search memories by content or tags"""
        try:
            # Load index
            with open(self.index_file, "r") as f:
                index = json.load(f)
            
            results = []
            for memory_entry in index["memories"]:
                # Check if memory matches search criteria
                memory_file = os.path.join(self.memory_dir, f"{memory_entry['id']}.json")
                
                if not os.path.exists(memory_file):
                    continue
                
                with open(memory_file, "r") as f:
                    memory = json.load(f)
                
                # Match by query (simple text search)
                if query and query.lower() in memory["content"].lower():
                    results.append(memory)
                    continue
                
                # Match by tags
                if tags:
                    if any(tag in memory["tags"] for tag in tags):
                        results.append(memory)
                        continue
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Limit results
            return results[:limit]
        except Exception as e:
            print(f"Error searching memories: {str(e)}")
            return []
    
    def get_recent_memories(self, limit=5):
        """Get the most recent memories"""
        try:
            # Load index
            with open(self.index_file, "r") as f:
                index = json.load(f)
            
            # Sort by timestamp (newest first)
            sorted_memories = sorted(index["memories"], key=lambda x: x["timestamp"], reverse=True)
            
            # Get full memory data for each entry
            results = []
            for memory_entry in sorted_memories[:limit]:
                memory_file = os.path.join(self.memory_dir, f"{memory_entry['id']}.json")
                if os.path.exists(memory_file):
                    with open(memory_file, "r") as f:
                        results.append(json.load(f))
            
            return results
        except Exception as e:
            print(f"Error retrieving recent memories: {str(e)}")
            return []

if __name__ == "__main__":
    # Test the memory manager
    memory_manager = MemoryManager()
    
    # Save a test memory
    success, memory_id = memory_manager.save_memory(
        "This is a test memory about Python programming.",
        tags=["test", "python"]
    )
    
    if success:
        print(f"Memory saved with ID: {memory_id}")
        
        # Retrieve the memory
        memory = memory_manager.get_memory(memory_id)
        print(f"Retrieved memory: {memory}")
        
        # Search memories
        results = memory_manager.search_memories(query="python")
        print(f"Search results: {results}")
        
        # Get recent memories
        recent = memory_manager.get_recent_memories(limit=3)
        print(f"Recent memories: {recent}")
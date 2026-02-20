import os
from pathlib import Path

class SandboxedFS:
    """
    A file system wrapper that absolutely prevents paths from traversing 
    outside of the approved target directory.
    """
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()

    def _resolve_and_verify(self, filepath: str) -> Path:
        """
        Resolves the given path and asserts it is strictly inside the root_dir.
        This prevents `../../` hallucination attacks.
        """
        requested_path = (self.root_dir / filepath).resolve()
        
        if not str(requested_path).startswith(str(self.root_dir)):
            raise PermissionError(
                f"SWARM VIOLATION: Agent attempted to access path {requested_path} "
                f"which is outside of the sandboxed root {self.root_dir}."
            )
        return requested_path

    def read_file(self, filepath: str) -> str:
        target = self._resolve_and_verify(filepath)
        if not target.exists():
            return f"Error: File {filepath} does not exist."
        return target.read_text(encoding="utf-8")

    def write_file(self, filepath: str, content: str) -> str:
        target = self._resolve_and_verify(filepath)
        # Ensure parent directories exist
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {filepath}"
    
    def list_files(self, directory: str = ".") -> str:
        target = self._resolve_and_verify(directory)
        if not target.exists() or not target.is_dir():
            return f"Error: Directory {directory} does not exist."
            
        tree = []
        for root, dirs, files in os.walk(target):
            # Skip hidden git folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            level = str(root).replace(str(target), '').count(os.sep)
            indent = ' ' * 4 * (level)
            tree.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                tree.append(f"{subindent}{f}")
        return "\n".join(tree)

    def read_codebase_outline(self, directory: str = ".") -> str:
        import ast
        target = self._resolve_and_verify(directory)
        if not target.exists() or not target.is_dir():
            return f"Error: Directory {directory} does not exist."
        
        outline = []
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.endswith('.py'):
                    filepath = Path(root) / f
                    # Algorithm safeguard: skip files larger than 1MB to prevent AST Memory crash
                    if filepath.stat().st_size > 1_000_000:
                        rel_path = filepath.relative_to(self.root_dir)
                        outline.append(f"File: {rel_path} (Skipped: Exceeds 1MB)")
                        continue
                    
                    rel_path = filepath.relative_to(self.root_dir)
                    try:
                        parsed = ast.parse(filepath.read_text(encoding="utf-8"))
                        classes = [n.name for n in parsed.body if isinstance(n, ast.ClassDef)]
                        funcs = [n.name for n in parsed.body if isinstance(n, ast.FunctionDef)]
                        if classes or funcs:
                            outline.append(f"File: {rel_path}")
                            if classes: outline.append(f"  Classes: {', '.join(classes)}")
                            if funcs: outline.append(f"  Functions: {', '.join(funcs)}")
                    except Exception as e:
                        outline.append(f"File: {rel_path} (Failed to parse: {e})")
        return "\n".join(outline) if outline else "No python files found or parsed."

    def read_file_chunk(self, filepath: str, start_line: int, end_line: int) -> str:
        target = self._resolve_and_verify(filepath)
        if not target.exists():
            return f"Error: File {filepath} does not exist."
        
        lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
        # Convert 1-indexed to 0-indexed slice
        chunk = lines[max(0, start_line - 1):end_line]
        return "".join([f"{i + start_line}: {line}" for i, line in enumerate(chunk)])

    def edit_file_chunk(self, filepath: str, start_line: int, end_line: int, new_content: str) -> str:
        target = self._resolve_and_verify(filepath)
        if not target.exists():
            return f"Error: File {filepath} does not exist. Use write_file for new files."
            
        lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
        
        if start_line < 1 or end_line > len(lines) + 1 or start_line > end_line:
             return "Error: Invalid line range specified."

        prefix = lines[:start_line - 1]
        suffix = lines[end_line:]
        
        # Ensure new content has proper newlines for joining
        new_lines = [line + '\n' for line in new_content.splitlines()]
        if new_content and not new_content.endswith('\n'):
            new_lines[-1] = new_lines[-1].rstrip('\n')  # Preserve if strict missing EOF newline
            
        new_file_content = "".join(prefix + new_lines + suffix)
        target.write_text(new_file_content, encoding="utf-8")
        return f"Successfully updated {filepath} from lines {start_line} to {end_line}"

    def search_codebase(self, query: str, top_k: int = 5) -> str:
        """
        Semantic RAG search over the entire codebase to find relevant snippets. 
        """
        try:
            import chromadb
            # For MVP, we do ephemeral on-the-fly indexing 
            # In production, this connects to a persistent Vector DB service
            client = chromadb.Client()
            collection = client.get_or_create_collection(name="codebase_rag")
            
            # Very basic on-the-fly index check (if empty, we index)
            if collection.count() == 0:
                docs = []
                metadatas = []
                ids = []
                doc_id = 0
                for root, dirs, files in os.walk(self.root_dir):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for f in files:
                        if f.endswith(('.py', '.md', '.ts', '.js', '.txt')):
                            filepath = Path(root) / f
                            # Safeguard against parsing massive non-code binaries or mega-logs
                            if filepath.stat().st_size > 5_000_000:
                                continue
                                
                            content = filepath.read_text(encoding="utf-8", errors='ignore')
                            
                            # Algorithmic Improvement: Semantic Chunking O(N) split instead of arbitrary slicing
                            paragraphs = content.split('\n\n')
                            chunks = []
                            current_chunk = []
                            current_length = 0
                            
                            for p in paragraphs:
                                p_len = len(p)
                                if current_length + p_len > 1000 and current_chunk:
                                    chunks.append("\n\n".join(current_chunk))
                                    current_chunk = [p]
                                    current_length = p_len
                                else:
                                    current_chunk.append(p)
                                    current_length += p_len
                            if current_chunk:
                                chunks.append("\n\n".join(current_chunk))
                            
                            for i, chunk in enumerate(chunks):
                                docs.append(chunk)
                                metadatas.append({"file": str(filepath.relative_to(self.root_dir)), "chunk": i})
                                ids.append(f"doc_{doc_id}")
                                doc_id += 1
                if docs:
                    collection.add(documents=docs, metadatas=metadatas, ids=ids)
            
            if collection.count() == 0:
                return "No indexable code found."
                
            results = collection.query(query_texts=[query], n_results=top_k)
            
            out = [f"--- Semantic Search Results for '{query}' ---"]
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                out.append(f"\nFile: {meta['file']} (Chunk {meta['chunk']}):\n{doc}\n")
            return "\n".join(out)
        except ImportError:
            return "Error: chromadb not installed. Semantic RAG disabled."
        except Exception as e:
            return f"Error during semantic search: {e}"

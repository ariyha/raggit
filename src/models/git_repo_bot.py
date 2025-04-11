"""
Core GitRepoBot class for analyzing Git repositories.
"""

import os
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import deque
from crewai import Agent, Task, Crew, Process, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config.settings import DEFAULT_GEMINI_MODEL, DEFAULT_TEMPERATURE, CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.file_utils import get_all_files, read_file, get_file_summaries
from src.agents.agents import (
    create_file_analyzer_agent,
    create_context_aggregator_agent,
    create_file_selector_agent,
    create_context_memory_agent
)

class GitRepoBot:
    def __init__(self, repo_path: str, gemini_model: str = DEFAULT_GEMINI_MODEL, temperature: float = DEFAULT_TEMPERATURE):
        """
        Initialize the Git Repository Bot with query-focused analysis
        
        Args:
            repo_path: Path to the git repository
            gemini_model: Gemini model to use
            temperature: Temperature for the model
        """
        self.repo_path = repo_path
        self.gemini_model = gemini_model
        self.temperature = temperature
        self.conversation_history = deque(maxlen=10)
        
        # Initialize Gemini model for Langchain
        self.llm = LLM(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini/gemini-2.0-flash",
        )
        
        # Text splitter for chunking large files
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        
        # Cache for file content to avoid re-reading
        self.file_cache = {}
        
        # Initialize agents
        self.file_analyzer_agent = create_file_analyzer_agent(self.llm)
        self.context_aggregator_agent = create_context_aggregator_agent(self.llm)
        self.file_selector_agent = create_file_selector_agent(self.llm)
        self.context_memory_agent = create_context_memory_agent(self.llm)

    def add_to_history(self, user_query: str, bot_response: str):
        """Store the latest interaction in the history."""
        self.conversation_history.append({"user": user_query, "bot": bot_response})

    def get_conversation_context(self):
        """Format the past conversation history for context."""
        return "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in self.conversation_history])
    
    def check_conversation_history(self, query: str) -> Tuple[bool, str]:
        """
        Check if the conversation history already contains information relevant to the current query
        
        Args:
            query: The user's query about the repository
            
        Returns:
            Tuple of (has_relevant_info, answer_from_history)
        """
        # If no conversation history, we need to search files
        if not self.conversation_history:
            return False, ""
        
        # Format conversation history for the agent
        conversation_context = self.get_conversation_context()
        
        task = Task(
            description=f"""
            CURRENT USER QUERY: {query}
            
            Based on the conversation history below, determine if the information needed to answer
            the current query is already present in previous responses.
            
            CONVERSATION HISTORY:
            {conversation_context}
            
            Your task:
            1. Analyze if the current query is related to topics already discussed
            2. Determine if previous responses contain sufficient information to answer the current query
            3. If the information exists, extract and synthesize it into a comprehensive answer
            4. If the information doesn't exist or is incomplete, indicate that new information is needed
            
            If you can answer the query from existing context, provide a complete answer.
            Otherwise, respond with "NEED_NEW_INFORMATION" to indicate that a file search is required.
            """,
            agent=self.context_memory_agent,
            expected_output="Either an answer from existing context or NEED_NEW_INFORMATION",
            llm=self.llm,
        )
        
        # Use a temporary crew to run the task
        temp_crew = Crew(
            agents=[self.context_memory_agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the task
        print("Checking if conversation history contains relevant information...")
        result = temp_crew.kickoff()
        
        # Extract the result
        result_value = list(result.values())[0] if isinstance(result, dict) else result
        result_str = str(result_value)
        
        # If the agent indicates we need new information
        if "NEED_NEW_INFORMATION" in result_str:
            return False, ""
        else:
            # The agent provided an answer from the conversation history
            return True, result_str
    
    def select_relevant_files(self, query: str) -> List[str]:
        """
        Use the file selector agent to determine which files are relevant to the query
        
        Args:
            query: The user's query about the repository
            
        Returns:
            List of file paths relevant to the query
        """
        file_summaries = get_file_summaries(self.repo_path, self.file_cache)

        print('Received Summaries')
        
        # Prepare a condensed version for the agent
        file_info = []
        for path, info in file_summaries.items():
            if "error" not in info:
                file_info.append(f"Path: {path}\nSize: {info['size']} bytes\nExtension: {info['extension']}\nPreview:\n{info['preview']}\n---")
        
        # Split files into batches if there are too many
        batch_size = 20
        file_batches = [file_info[i:i + batch_size] for i in range(0, len(file_info), batch_size)]
        
        all_selected_files = []
        
        for batch_idx, file_batch in enumerate(file_batches):
            print(f"Processing batch {batch_idx + 1} of {len(file_batches)}...")
            batch_info = "\n".join(file_batch)
            
            task = Task(
                description=f"""
                QUERY: {query}
                
                Based on the user's query above, analyze the following list of files in the repository
                and select ONLY those that are likely to contain information relevant to answering this query.
                
                Repository files (batch {batch_idx + 1} of {len(file_batches)}):
                {batch_info}
                
                Return ONLY a list of file paths that are relevant to the query, one per line.
                Focus on being precise - only include files that are truly relevant.
                If no files in this batch seem relevant, return "No relevant files found in this batch."
                """,
                agent=self.file_selector_agent,
                expected_output="A list of file paths relevant to the query",
                llm=self.llm,
            )
            
            # Use a temporary crew to run the task
            temp_crew = Crew(
                agents=[self.file_selector_agent],
                tasks=[task],
                verbose=True,
                process=Process.sequential
            )
            
            # Run the task
            print("Running file selector agent...")
            result = temp_crew.kickoff()
            print(f"File selection result: {result}")

            # Extract the result - may vary based on crewai version
            result_value = list(result.values())[0] if isinstance(result, dict) else result
            
            # Extract file paths from the result
            selected_files = []
            for line in str(result_value).split('\n'):
                line = line.strip()
                for path in file_summaries:
                    # Check if the line contains or exactly matches a file path
                    if path == line or f"Path: {path}" in line:
                        selected_files.append(path)
                        break
            
            all_selected_files.extend(selected_files)
        
        # If we didn't find any relevant files, include some default files
        if not all_selected_files and file_summaries:
            # Include up to 5 files as fallback
            all_selected_files = list(file_summaries.keys())[:5]
            
        return all_selected_files
    
    def analyze_files_for_query(self, query: str, selected_files: List[str]) -> Dict[str, str]:
        """
        Analyze selected files specifically in the context of the query
        
        Args:
            query: The user's query about the repository
            selected_files: List of files to analyze
            
        Returns:
            Dictionary mapping file paths to their analyses
        """
        file_paths = get_all_files(self.repo_path)
        file_analyses = {}

        # Create file analysis tasks
        file_tasks = []
        for relative_path in selected_files:
            if relative_path not in file_paths:
                continue
                
            full_path = file_paths[relative_path]
            content = read_file(full_path, self.file_cache)

            # Skip empty or unreadable files
            if not content or content.startswith("Error reading file"):
                continue

            # Handle large files by taking key parts
            if len(content) > 60000:
                chunks = self.text_splitter.split_text(content)
                if len(chunks) >= 3:
                    content_sample = (
                        f"\n\n--- BEGINNING OF FILE ---\n\n{chunks[0]}"
                        f"\n\n--- MIDDLE OF FILE ---\n\n{chunks[len(chunks)//2]}"
                        f"\n\n--- END OF FILE ---\n\n{chunks[-1]}"
                    )
                else:
                    content_sample = "\n\n".join(chunks[:3])  # Take first few chunks
            else:
                content_sample = content

            task = Task(
                description=f"""
                USER QUERY: {query}
                
                Analyze the following file IN THE CONTEXT OF THE USER QUERY:
                File: {relative_path}
                
                File content:
                ```
                {content_sample}
                ```
                
                Focus ONLY on extracting information that helps answer the user's query.
                Ignore irrelevant parts of the file. Be concise and specific. If there is no relevant information, return nothing.
                
                Include:
                1. Relevant code sections (with line numbers if possible)
                2. Explanation of how this file relates to the query
                3. Important functions, classes, or variables that address the query
                
                If this file doesn't contain relevant information for the query, state that briefly.
                """,
                agent=self.file_analyzer_agent,
                expected_output=f"Query-relevant analysis of {relative_path}",
                llm=self.llm,
            )
            file_tasks.append(task)

        if file_tasks:
            # Create and run the crew for file analysis
            file_crew = Crew(
                agents=[self.file_analyzer_agent],
                tasks=file_tasks,
                verbose=True
            )

            # Start analysis
            file_results = file_crew.kickoff()

            # Process results
            for task, result in zip(file_tasks, file_results):
                match = re.search(r"analysis of (.+)", task.expected_output)
                if match:
                    file_path = match.group(1)
                    file_analyses[file_path] = result

        return file_analyses
        
    def aggregate_analyses(self, query: str, file_analyses: Dict[str, str]) -> str:
        """
        Aggregate the file analyses to answer the query
        
        Args:
            query: The user's query about the repository
            file_analyses: Dictionary mapping file paths to their analyses
            
        Returns:
            Comprehensive answer to the query
        """
        # Format the file analyses for the aggregator
        analyses_text = ""
        if file_analyses:
            for file_path, analysis in file_analyses.items():
                analyses_text += f"\n\n--- ANALYSIS OF {file_path} ---\n{analysis}"
        
        task = Task(
            description=f"""
            USER QUERY and HISTORY: {query}
            
            Based on the analyses of relevant files below, provide a comprehensive answer to the user's query.
            Synthesize information from all the file analyses, focusing on directly addressing what the user wants to know.
            If it is a common knowledge question, provide a general answer based on the codebase context.
            
            File analyses:
            {analyses_text}
            
            Your response should:
            1. Directly answer the query with relevant details from the codebase
            2. Reference specific files/functions/classes when appropriate
            3. Be clear, concise, and well-organized
            4. Include code examples where helpful
            
            Do not repeat all the file analyses - synthesize the information to provide a unified, coherent answer.
            """,
            agent=self.context_aggregator_agent,
            expected_output="A comprehensive answer to the user's query",
            llm=self.llm,
        )
        
        crew = Crew(agents=[self.context_aggregator_agent], tasks=[task])
        result = crew.kickoff()

        return result

    def answer_query(self, query: str) -> str:
        """
        Process a query about the repository with context-based file analysis,
        first checking if the conversation history already contains the answer
        
        Args:
            query: The user's question about the repository
            
        Returns:
            A comprehensive answer based on relevant files in the repository or from conversation history
        """
        print(f"Processing query: {query}")
        
        # First check if we already have relevant information in conversation history
        has_relevant_info, answer_from_history = self.check_conversation_history(query)

        
        # Add conversation context to the query for better contextual understanding
        context = self.get_conversation_context()
        full_query = f"Previous conversation:\n{context}\n\nCurrent user query:\n{query}" if context else query

        if has_relevant_info:
            print("Found relevant information in conversation history")
            answer = self.aggregate_analyses(full_query, {})
            self.add_to_history(query, answer)
            return answer, "PREVIOUS CONTEXT USED"
        
        # Step 1: Select relevant files for the query
        print(f"Selecting relevant files for query")
        relevant_files = self.select_relevant_files(full_query)
        print(f"Selected {len(relevant_files)} relevant files")

        context = "" 
        context += f"--- SELECTED FILES ---\n{relevant_files}\n"
        
        # Step 2: Analyze the selected files in the context of the query
        print("Analyzing selected files...")
        file_analyses = self.analyze_files_for_query(full_query, relevant_files)
        print(f"Completed analysis of {len(file_analyses)} files")

        context += f"--- ANALYSES ---\n{file_analyses}\n"
        
        # Step 3: Aggregate analyses to answer the query
        print("Aggregating analyses to answer query...")
        answer = self.aggregate_analyses(full_query, file_analyses)
        
        # Store the interaction in conversation history
        self.add_to_history(query, answer)
        
        return answer, context
"""
Agent creation functions for the GitRepoBot application.
"""

from crewai import Agent, LLM

def create_file_analyzer_agent(llm: LLM) -> Agent:
    """
    Create an agent that analyzes individual files based on the query
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        File analyzer agent
    """
    return Agent(
        role="Query-Focused File Analyzer",
        goal="Analyze code files to extract information specifically relevant to the user's query",
        backstory="""You are an expert code analyst specializing in query-relevant information
        extraction. When given a specific question about code, you can quickly analyze files and
        extract only the parts that are relevant to answering that question. You understand multiple
        programming languages and can identify patterns, functions, classes, and components that
        relate to the query.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
def create_context_aggregator_agent(llm: LLM) -> Agent:
    """
    Create an agent that aggregates context from multiple files to answer a specific query
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Context aggregator agent
    """
    return Agent(
        role="Query-Focused Context Aggregator",
        goal="Combine relevant file analyses into a comprehensive answer to the user's query",
        backstory="""You are a systems architect who excels at synthesizing information from
        multiple sources to answer specific questions. You can take query-relevant information
        from individual code files and create a coherent, targeted response that directly
        addresses what the user wants to know about the codebase.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
def create_file_selector_agent(llm: LLM) -> Agent:
    """
    Create an agent that selects which files are likely relevant to a query
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        File selector agent
    """
    return Agent(
        role="File Relevance Selector",
        goal="Determine which files in the repository are most likely to contain information relevant to the query",
        backstory="""You are an expert at quickly identifying which parts of a codebase are most
        likely to be relevant to specific questions. By examining file names, paths, and brief snippets,
        you can efficiently determine which files should be analyzed in depth to answer a particular query,
        saving time and computational resources.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_context_memory_agent(llm: LLM) -> Agent:
    """
    Create an agent that checks if conversation history already contains the answer to a query
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Context memory agent
    """
    return Agent(
        role="Conversation Context Analyzer",
        goal="Determine if the conversation history already contains information relevant to the current query",
        backstory="""You are a knowledge management expert specializing in contextual memory and information retrieval.
        You have an exceptional ability to recall relevant information from past conversations and determine whether a new
        query can be answered with existing context or requires new information. You understand how to identify when a query
        is related to previous topics and can extract and synthesize relevant information from conversation history to avoid
        redundant searches.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


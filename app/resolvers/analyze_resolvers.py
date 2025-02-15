import hashlib
import logging
from typing import List
from fastapi import HTTPException
from app.packages.models.conversation_models import AnalayzeRequest, AnalyzeQuery
from app.openai_resolvers.keyword_extraction import (
    create_prompt_for_single_sentence, 
    create_prompts_for_multiple_sentences, 
    fetch_keywords_from_api, 
    fetch_keywords_from_api_only_one
)
from app.packages.mongodb import (
    get_analyze, 
    get_conversation_by_id,
    store_keywords, 
    update_or_append_field_by_id, 
    get_analysis_summary_by_sha,
    fetch_user_data_from_db
)
from app.services.add_new_label import add_new_label
from app.services.analyze_service import get_attribute_and_explanation_object_array
from app.services.consolidate_values import consolidate_values
from app.type import Conversation, FlattenedAnalysisSummary, LabeledAttribute

logger = logging.getLogger(__name__)

async def process_answer_resolver(request: AnalayzeRequest):
    try:
        first_conversation_id = request.conversation_id
        query = AnalyzeQuery(conversation_id=first_conversation_id)
        user_conversation = await get_analyze(query)
        analyze = [analyze for analyze in user_conversation.analyze if analyze["role"] == "assistant"]
        return analyze
        
    except Exception as e:
        logger.error(f"Error in process_answer_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_retrieve_keywords_resolver(request: AnalayzeRequest):
    try:
        first_conversation_id = request.conversation_id
        query = AnalyzeQuery(conversation_id=first_conversation_id)
        user_conversation = await get_analyze(query)
        analyze = [analyze['content'] for analyze in user_conversation.analyze if analyze["role"] == "assistant"]

        if hasattr(user_conversation, 'keywords') and user_conversation.keywords:
            keywords = [keyword for keyword in user_conversation.keywords]
        else:
            keywords = [] 

        if len(analyze) > len(keywords):
            missing_analyze = analyze[len(keywords):]
            prompts = create_prompts_for_multiple_sentences(missing_analyze)
            
            responses = await fetch_keywords_from_api(prompts)
            new_keywords = [response.choices[0].message.content.strip() for response in responses]
            
            keywords.extend(new_keywords)
            
            await store_keywords(first_conversation_id, keywords)

            return keywords
        
    except Exception as e:
        logger.error(f"Error in process_retrieve_keywords_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Removed get_all_questions_resolver and get_question_resolver functions

async def get_analyze_resolver(conversation_id: str):
    """
    Fetches and analyzes the conversation by extracting keywords from summaries.
    Returns existing analysis if SHA matches, otherwise generates new analysis.

    Args:
        conversation_id (str): The ID of the conversation to analyze.

    Returns:
        str: The analysis summary.

    Raises:
        HTTPException: If there is an error during data fetching or processing.
    """
    try:
        user_conversation = await get_conversation_by_id(conversation_id)
        
        # Combine all assistant summaries
        summaries_content = " ".join(
            summary['content'] 
            for summary in user_conversation['summaries'] 
            if summary["role"] == "assistant"
        )

        # Generate SHA-256 hash of the combined summaries
        sha256_hash = hashlib.sha256(summaries_content.encode('utf-8')).hexdigest()
        
        # Try to get existing analysis summary
        existing_summary = await get_analysis_summary_by_sha(conversation_id, sha256_hash)
        
        if (existing_summary):
            return existing_summary
            
        # If no existing summary, generate new one
        prompts = create_prompt_for_single_sentence(summaries_content)
        api_response = await fetch_keywords_from_api_only_one(prompts)
        analysis_summary_text = api_response.choices[0].message.content.strip()
        analyzed_values = get_attribute_and_explanation_object_array(analysis_summary_text)
        
        value_object = {
            "analysis_summary_text": analysis_summary_text,
            "analyzed_values": analyzed_values
        }
        
        # Store the new analysis summary
        await update_or_append_field_by_id(
            conversation_id=conversation_id,
            field_name="analysis_summaries",
            key=sha256_hash,
            value=value_object
        )
        
        return value_object
        
    except Exception as error:
        logger.error(f"Error in get_analyze_resolver: {error}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

async def extract_analysis_summaries(user_data: List[Conversation]) -> List[FlattenedAnalysisSummary]:
    """
    Extracts and flattens analysis summaries from user data.

    Args:
        user_data (list): List of user conversations.

    Returns:
        list: Flattened list of analyzed values from the latest analysis summaries.
    """
    all_analysis_summaries = []
    for conversation in user_data:
        conversation_id = conversation["_id"]
        user_conversation = await get_conversation_by_id(conversation_id)
        if user_conversation and "analysis_summaries" in user_conversation:
            # Get the last analysis summary object
            analysis_summaries = list(user_conversation["analysis_summaries"].values())
            last_summary_object = analysis_summaries[-1]
            # Extract the 'analyzed_values' from the last summary object
            analyzed_values = last_summary_object['analyzed_values']
            all_analysis_summaries.extend(analyzed_values)
    return all_analysis_summaries

async def get_consolidated_and_labeled_values_for_user(user_id: str) -> List[LabeledAttribute]:
    """
    Retrieves all analysis summaries belonging to a specific user by first getting all conversation IDs
    and then retrieving the values using those IDs. The function consolidates and labels the values
    before returning them. Ignores conversations without analysis summaries.

    Args:
        user_id (str): The ID of the user whose analysis summaries are to be retrieved.

    Returns:
        list: List of consolidated and labeled analysis summaries.

    Raises:
        HTTPException: If there is an error during data fetching or processing.
    """
    try:
        user_conversations = await fetch_user_data_from_db(user_id)
        
        if not len(user_conversations):
            return []
        
        flattened_analysis_summaries = await extract_analysis_summaries(user_conversations)
        consolidated_data = consolidate_values(flattened_analysis_summaries)
        labeled_data = add_new_label(consolidated_data)
        
        return labeled_data
    except ValueError as ve:
        logger.warning(ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Resolver error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

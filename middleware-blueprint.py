async def secure_llm_call(user_input):
    # 1. PRE-PROCESS: Scan Input
    is_safe, reason = scan_with_llama_guard(user_input, role="user")
    if not is_safe:
        return {"error": "Security violation", "code": reason}

    # 2. CORE: Call Main LLM
    raw_response = await call_gpt4(user_input)

    # 3. POST-PROCESS: Scan & Redact Output
    # Check for PII in the generated response
    redacted_response = presidio_analyzer.anonymize(raw_response)
    
    # Check for toxic output
    is_safe_out, _ = scan_with_llama_guard(redacted_response, role="assistant")
    if not is_safe_out:
        return {"error": "Response generated unsafe content"}

    return {"response": redacted_response}
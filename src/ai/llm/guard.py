# from guardrails.hub import ToxicLanguage, DetectJailbreak
# from guardrails import Guard

# def guard(input_text):

#     guard = Guard().use_many(
#         ToxicLanguage(),
#         DetectJailbreak()
#     )

#     try:
#         validation_results = guard.parse(
#             input_text
#         )
#         if validation_results:
#             return True
#     except Exception as e:
#         raise ValueError("Error while validation using guardrails")
    


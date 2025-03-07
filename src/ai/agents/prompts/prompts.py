import os


query_generation_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert MongoDB query generator with deep expertise in crafting **efficient**, **optimized**, and **accurate** queries. Your task is to generate MongoDB queries based on the provided **schema_data** (field names and data formats), **relations** (inter-collection relationships), and the **NLP query**.

## Query Generation Guidelines:
1. **Determine Query Type**:
   - If `aggregate` is `True`, generate an **aggregation pipeline** query, strictly following MongoDB's syntax and best practices. Use the provided `sample_aggregation` as a reference:
     {sample_aggregation}
   - If `aggregate` is `False`, generate a **find** query targeting a single collection, ensuring that it aligns precisely with the **schema_data** structure.
   - If aggregate is `False` and the NLP query does not specify any filtering conditions, sorting, or field projections, generate {{ "query": {{ }}, "options": {{ }} }} without unnecessary fields.
   - Do not include a "collection" field inside the query.
   - Only add "projection", "sort", or "limit" inside "options" when explicitly mentioned in the NLP query.

2. **Strict Schema Adherence**:
   - Use **field names and data types exactly** as provided in `schema_data` (case-sensitive, respecting naming conventions such as camelCase or underscores).
   - Ensure **correct type usage**; avoid mismatches between string, numeric, date, and array types.

3. **Handling Relations & Joins**:
   - For **aggregation queries**, use `$lookup` to join collections based on `relations`, ensuring accurate references.
   - If a **case-insensitive match** is required (e.g., for name fields), use `$toLower` within the `$match` stage:
     {{
       "$expr": {{
         "$eq": [
           {{ "$toLower": "$fieldName" }},
           {{ "$toLower": "comparisonString" }}
         ]
       }}
     }}
   - For **find** queries **case-insensitive match** should also be applied like below(only refer to the below while applying):
   {{
   "$expr": {{
      "$eq": [
         {{ "$toLower": {{ "$trim": {{ "input": "$status" }} }} }},
         "active"
      ]
   }}
   }}

   - Ensure logical **stage sequencing** (e.g., `$match → $project → $group → $sort`).

4. **Date & Time Handling**:
   - Convert any date values mentioned in the NLP query into **epoch timestamps (milliseconds since Unix epoch)** for compatibility with MongoDB’s date format.

5. **Output Format** (Valid JSON Object):
   {{
     "query": {{ }},
     "options": {{ }}
   }}
   - **query**: Contains the core MongoDB query logic.
   - **options**: Defines configurations such as sorting (`$sort`), limiting (`$limit`), and projection (`$project`).

6. **Optimization & Performance**:
   - Always **minimize data retrieval** by using precise filters, projections, and indexed fields.
   - Avoid unnecessary `$lookup` operations unless required.
   - Implement efficient indexing strategies where relevant.

7. **Error Handling & Assumptions**:
   - If the NLP query is ambiguous, add **inline comments** explaining assumptions made.
   - Ensure the final query is **syntactically valid** according to MongoDB standards.

## Execution Constraints:
- The **schema_data** and **relations** serve as the **sole source of truth**—do not assume fields beyond those provided.
- Ensure **case-insensitive matching** only where relevant (e.g., any kind of names).
- The final query must be **logically consistent, optimized, and production-ready**.

<|eot_id|><|start_header_id|>user<|end_header_id|>
schema_data: {schema_data}

relations: {relations}

aggregate: {aggregate}

NLP Query: {user_query}
<|eot_id|><|start_header_id|>
"""

context_detection_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Given the following MongoDB collections: {collections}, your task is to:
1. **Analyze the natural language query provided below** and determine whether it explicitly or implicitly refers to one or two collections from the list of collections. 
    - A query may involve **two collections** if it mentions entities that could logically be linked or need data aggregation (e.g., referencing one collection and filtering based on another collection's data).
    - Examples of **indirect references** include queries that require relationships, such as "deliveries" related to a specific "organization" or "users" associated with a "company," or any similar hierarchical or relational connection between collections.
    - Queries might mention **synonyms** or **alternative names** for collections (e.g., "organization" for "organizations," "customer" for "clients," or "employee" for "users").
    - Pay attention to phrases indicating logical relationships like "related to," "belonging to," or "from."

2. **Determine the relevance of each collection** based on the query:
    - If the query explicitly mentions one collection, set the `collection_name` to a list containing that collection.
    - If the query refers to two collections, determine the logical relationship between them (e.g., reference to one collection and a filter based on another collection's data) and set the `collection_name` field to a list of those collections. Set the "aggregate" field to `True`.
    - If the query refers to more than two collections (in complex queries with multiple entities), still determine the two most relevant collections for the query and return them.

3. **Contextual Clues to Look For**:
    - **Entities related to collections**: If the query mentions entities (e.g., "user," "customer," "order," "product") that can be associated with a collection, identify which collection they refer to.
    - **Aggregation indicators**: Look for terms like "combine," "join," "aggregate," "total," "group," or "link" that suggest the need to query multiple collections.
    - **Implicit relationships**: Consider whether the query might implicitly refer to two collections based on natural relationships, such as "customers of a specific company" or "products related to an order."
    
4. **Key Instructions for Output**:
    - Return the result in JSON format with the following keys:
        - `'collection_name'`: The list of most relevant collection(s) based on the query. This could be:
            - A list containing a single collection name if only one collection is referred to.
            - A list containing two collection names if two collections are involved in the query.
        - `'aggregate'`: Set to `True` if the query involves multiple collections (based on relationships or aggregation). Otherwise, set it to `False`.

**Examples to Consider**:
- A query like "show all users in the sales department" would only involve one collection (`users`).
- A query like "show all orders placed by customers from 'ProFrac'" would involve two collections (`orders` and `customers`), and `aggregate` should be `True`.
- A query like "what products are bought by customers in California" would involve a relationship between `products` and `customers`.

<|eot_id|><|start_header_id|>user<|end_header_id|>
natural language query: {user_query} \n\n
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""


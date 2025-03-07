import pandas as pd
import ast  # For safely evaluating string representations of Python literals


# Load the Excel file
def excel_to_dataframe(file_path):
    # Load the Excel file

    df = pd.read_excel(file_path)

    # Drop rows with missing values in critical columns (Module, Field, Type)
    df = df.dropna(subset=['Collection', 'Field', 'Type', 'Annotation'])

    # Initialize the dictionary
    data = {
        'collection_name': [],
        'fields': [],
        'Annotation': []
    }

    # Iterate over the rows of the cleaned DataFrame
    for _, row in df.iterrows():
        collection = row['Collection'].strip()  # Remove leading/trailing spaces
        field_name = row['Field'].strip()
        dtype = row['Type'].strip()
        Annotation = row['Annotation'].strip()

        # Add collection name if not already in the list
        data['collection_name'].append(collection)
        data['Annotation'].append(Annotation)

        # Add fields in the required format
        field_dict = f"{{'name': '{field_name}', 'dtype': '{dtype}'}}"
        data['fields'].append(field_dict)

    # Print the resulting dictionary to verify the lengths of the arrays
    print("\nResulting Dictionary:")
    print(data)

    # Verify if the lengths of 'collection_name' and 'fields' are equal
    if len(data['collection_name']) == len(data['fields']):
        print("\nThe arrays are equal in length.")
    else:
        print("\nThe arrays are not equal in length.")

    metadata_df = pd.DataFrame(data)

    return metadata_df


def metadata_to_text(metadata_df: pd.DataFrame):
    descriptions = []

    # Iterate through each row in the DataFrame
    for index, row in metadata_df.iterrows():
        collection_name = row['collection_name']  # Column containing collection name
        field_string = row['fields']  # Column containing the fields string
        Annotation = row['Annotation']  # Column containing the Annotation string

        try:
            # Safely evaluate the string representation of a dictionary
            fields = ast.literal_eval(field_string)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing fields for collection '{collection_name}': {e}")
            continue

        # Create a string description of the fields
        field_descriptions = ', '.join([f"{name} ({dtype})" for name, dtype in fields.items()])
        description = f"Collection: {collection_name}, Fields: {field_descriptions},Annotation: {Annotation}"

        descriptions.append({
            'collection_name': collection_name,
            'description': description
        })

    return descriptions


# Example usage
if __name__ == "__main__":
    file_path=r"C:\Users\WalkingTree\Downloads\User.xlsx"
    metadata_df = excel_to_dataframe(file_path)
    descriptions = metadata_to_text(metadata_df)


    # Print the generated descriptions
    for item in descriptions:
        #         print(f"collection_name: {item['collection_name']}, Description: {item['description']}")
        print(f" Description: {item['description']}")

# Print the resulting dictionary to verify the lengths of the arrays
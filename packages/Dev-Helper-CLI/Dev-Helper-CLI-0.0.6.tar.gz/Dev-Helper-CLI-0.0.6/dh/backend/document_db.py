import json

class DocumentDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            return {}

    def save(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get_document(self, document_id: str):
        return self.data.get(document_id)
    
    def filter_documents(self, filter_func):
        filtered_documents = []
        for document_id, document_data in self.data.items():
            if filter_func(document_data):
                filtered_documents.append(
                    (document_id, document_data))
        return filtered_documents

    def add_document(self, document_id: str, document_data: list[dict]):
        self.data[document_id] = document_data

    def update_document(self, document_id: str, updated_data: list[dict]):
        if document_id in self.data:
            self.data[document_id].update(updated_data)
        else:
            raise ValueError(
            f"Document with ID '{document_id}' does not exist.")

    def delete_document(self, document_id: str):
        if document_id in self.data:
            del self.data[document_id]
        else:
            raise ValueError(
            f"Document with ID '{document_id}' does not exist.")
                
        


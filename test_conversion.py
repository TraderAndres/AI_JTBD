# test_conversion.py
from utils import save_hierarchy_to_text

def test_conversion():
    json_input = "Finance_hierarchy.json"
    text_output = "Finance_hierarchy_output.txt"
    save_hierarchy_to_text(json_input, text_output)
    print(f"Hierarchical text saved to '{text_output}'.")

if __name__ == "__main__":
    test_conversion()

# test_conversion.py
from utils import save_hierarchy_to_markdown

def test_conversion():
    json_input = "Finance_hierarchy.json"
    text_output = "Finance_hierarchy_output.md"
    save_hierarchy_to_markdown(json_input, text_output)
    print(f"Hierarchical text saved to '{text_output}'.")

if __name__ == "__main__":
    test_conversion()

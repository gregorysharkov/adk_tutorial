# Company Data Transformation Scripts

This directory contains scripts to transform company data from CSV format into the same format as `company_qa_eval_100.jsonl`.

## Files

- `transform_companies.py` - Main transformation script
- `test_transformation.py` - Test script to verify the transformation works
- `README.md` - This documentation file

## Usage

### 1. Transform Companies (Full Dataset)

To transform the full company dataset using Poetry:

```bash
poetry run transform-companies
```

Or manually:
```bash
cd app/scratchfiles
python transform_companies.py
```

This will:
- Read from `data/datasets/external/companies-2023-q4-sm.csv`
- Generate QA pairs for 100 randomly sampled companies
- Save output to `data/datasets/transformed_companies_qa.jsonl`

### 2. Test Transformation

To test the transformation with a small sample using Poetry:

```bash
poetry run test-transform
```

Or manually:
```bash
cd app/scratchfiles
python test_transformation.py
```

This will:
- Process only 10 companies for quick testing
- Save output to `data/datasets/test_transformed_companies.jsonl`
- Show a preview of the generated QA pairs

### 3. Custom Transformation

You can also use the functions programmatically:

```python
from transform_companies import transform_companies_to_qa_format

# Transform with custom parameters
transform_companies_to_qa_format(
    csv_path="path/to/input.csv",
    output_path="path/to/output.jsonl",
    sample_size=50
)
```

## Output Format

The script generates QA pairs in the same format as `company_qa_eval_100.jsonl`:

```json
{
    "id": "q001",
    "company": "Company Name",
    "question": "What does the company do?",
    "expected_answer": "Company Name is a company that operates in the industry industry, specializing in company_type.",
    "references": []
}
```

## Generated Questions

For each company, the script generates these standard questions:
1. What does the company do?
2. Which industry does the company operate in?
3. What type of company is it?
4. Where is the company located?

**Website Questions:**
5. What is the company's website?
6. Does the company have an online presence?
7. Where can I find more information about this company online?
8. What is the company's web address?

*Note: For companies with websites, these questions provide the actual website information. For companies without websites, these questions return "not available" responses.*

Additional questions are generated if the data contains:
- Founding year
- Website URL (generates 4 website-related questions)
- Company size

**Companies without websites** also get 4 website-related questions with "not available" responses, ensuring comprehensive coverage.

## Data Requirements

The input CSV should have these columns:
- `name` - Company name
- `industry` - Industry classification
- `type` - Company type (e.g., Corporation, Partnership, Nonprofit)
- `city` - City location
- `state` - State/province location
- `founded` - Founding year (optional)
- `website` - Company website (optional)
- `size` - Company size/employee count (optional)

## Notes

- The script filters out companies with missing essential information
- A random seed (42) is used for reproducible sampling
- The script handles missing data gracefully by using "unknown" placeholders
- Output is saved in JSONL format for easy processing

## Integration with Evaluation Runner

The transformed dataset is automatically integrated with the evaluation runner:

- **Original dataset**: 700 QA pairs (100 companies × 7 questions each)
- **Transformed dataset**: 969 QA pairs (100 companies × 9-10 questions each)
- **Combined total**: 1,669 QA pairs for comprehensive evaluation

The evaluation runner can now process both datasets simultaneously using:
```python
from app.evaluation.runner import run_evaluation_on_combined_datasets

# Run evaluation on both datasets
run_evaluation_on_combined_datasets(version="v001")
```

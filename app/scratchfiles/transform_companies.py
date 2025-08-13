#!/usr/bin/env python3
"""
Script to transform company data from CSV format into the same format as company_qa_eval_100.jsonl.

This script reads a CSV file containing company information and generates QA pairs
in the same format as the evaluation dataset.
"""

import csv
import json
import random
from pathlib import Path
from typing import Any


def load_companies_from_csv(
    csv_path: str, sample_size: int = 100
) -> list[dict[str, Any]]:
    """
    Load companies from CSV file and return a sample.

    Args:
        csv_path: Path to the CSV file
        sample_size: Number of companies to sample

    Returns:
        list of company dictionaries
    """
    companies = []

    with open(csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Filter out companies with missing essential information
            if row.get("name") and row.get("industry") and row.get("type"):
                companies.append(row)

    # Randomly sample companies
    if len(companies) > sample_size:
        companies = random.sample(companies, sample_size)

    return companies


def generate_qa_pairs(company: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate QA pairs for a given company.

    Args:
        company: Company information dictionary

    Returns:
        list of QA pair dictionaries
    """
    qa_pairs = []

    # Standard questions that work for most companies
    questions = [
        {
            "question": "What does the company do?",
            "template": "{} is a company that operates in the {} industry, specializing in {}.",
        },
        {
            "question": "Which industry does the company operate in?",
            "template": "The company operates in the {} industry.",
        },
        {"question": "What type of company is it?", "template": "It is a {} company."},
        {
            "question": "Where is the company located?",
            "template": "The company is located in {}, {}.",
        },
    ]

    # Generate answers based on available company data
    for i, q_info in enumerate(questions):
        company_name = company.get("name", "Unknown Company")
        industry = company.get("industry", "unknown industry")
        company_type = company.get("type", "unknown type")
        city = company.get("city", "unknown city")
        state = company.get("state", "unknown state")

        if q_info["question"] == "What does the company do?":
            answer = q_info["template"].format(company_name, industry, company_type)
        elif q_info["question"] == "Which industry does the company operate in?":
            answer = q_info["template"].format(industry)
        elif q_info["question"] == "What type of company is it?":
            answer = q_info["template"].format(company_type)
        elif q_info["question"] == "Where is the company located?":
            answer = q_info["template"].format(city, state)
        else:
            answer = "Information not available."

        qa_pair = {
            "id": f"q{len(qa_pairs) + 1:03d}",
            "company": company_name,
            "question": q_info["question"],
            "expected_answer": answer,
            "references": [],
        }
        qa_pairs.append(qa_pair)

    # Add company-specific questions if we have additional data
    if company.get("founded"):
        qa_pair = {
            "id": f"q{len(qa_pairs) + 1:03d}",
            "company": company_name,
            "question": "When was the company founded?",
            "expected_answer": f"The company was founded in {company['founded']}.",
            "references": [],
        }
        qa_pairs.append(qa_pair)

    if company.get("website"):
        # Basic website question
        qa_pair = {
            "id": f"q{len(qa_pairs) + 1:03d}",
            "company": company_name,
            "question": "What is the company's website?",
            "expected_answer": f"The company's website is {company['website']}.",
            "references": [],
        }
        qa_pairs.append(qa_pair)

        # Additional website-related questions
        website_questions = [
            {
                "question": "Does the company have an online presence?",
                "answer": f"Yes, the company has a website at {company['website']}.",
            },
            {
                "question": "Where can I find more information about this company online?",
                "answer": f"You can visit their website at {company['website']} for more information.",
            },
            {
                "question": "What is the company's web address?",
                "answer": f"The company's web address is {company['website']}.",
            },
        ]

        for q_info in website_questions:
            qa_pair = {
                "id": f"q{len(qa_pairs) + 1:03d}",
                "company": company_name,
                "question": q_info["question"],
                "expected_answer": q_info["answer"],
                "references": [],
            }
            qa_pairs.append(qa_pair)
    else:
        # Add questions for companies without websites
        no_website_questions = [
            {
                "question": "What is the company's website?",
                "answer": "The company's website information is not available.",
            },
            {
                "question": "Does the company have an online presence?",
                "answer": "The company's online presence information is not available.",
            },
            {
                "question": "Where can I find more information about this company online?",
                "answer": "Online information about this company is not available.",
            },
            {
                "question": "What is the company's web address?",
                "answer": "The company's web address is not available.",
            },
        ]

        for q_info in no_website_questions:
            qa_pair = {
                "id": f"q{len(qa_pairs) + 1:03d}",
                "company": company_name,
                "question": q_info["question"],
                "expected_answer": q_info["answer"],
                "references": [],
            }
            qa_pairs.append(qa_pair)

    if company.get("size"):
        qa_pair = {
            "id": f"q{len(qa_pairs) + 1:03d}",
            "company": company_name,
            "question": "What is the company size?",
            "expected_answer": f"The company has {company['size']} employees.",
            "references": [],
        }
        qa_pairs.append(qa_pair)

    return qa_pairs


def transform_companies_to_qa_format(
    csv_path: str, output_path: str, sample_size: int = 100
) -> None:
    """
    Transform companies from CSV to QA format and save to JSONL file.

    Args:
        csv_path: Path to input CSV file
        output_path: Path to output JSONL file
        sample_size: Number of companies to process
    """
    print(f"Loading companies from {csv_path}...")
    companies = load_companies_from_csv(csv_path, sample_size)
    print(f"Loaded {len(companies)} companies")

    all_qa_pairs = []

    for company in companies:
        qa_pairs = generate_qa_pairs(company)
        all_qa_pairs.extend(qa_pairs)

    print(f"Generated {len(all_qa_pairs)} QA pairs")

    # Save to JSONL format
    with open(output_path, "w", encoding="utf-8") as file:
        for qa_pair in all_qa_pairs:
            file.write(json.dumps(qa_pair, ensure_ascii=False) + "\n")

    print(f"Saved QA pairs to {output_path}")


def main():
    """Main function to run the transformation."""
    # Set random seed for reproducible results
    random.seed(42)

    # File paths - use Path to handle relative paths correctly
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    csv_path = (
        project_root / "data" / "datasets" / "external" / "companies-2023-q4-sm.csv"
    )
    output_path = project_root / "data" / "datasets" / "transformed_companies_qa.jsonl"

    # Ensure input file exists
    if not Path(csv_path).exists():
        print(f"Error: Input file {csv_path} not found!")
        return

    # Create output directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Transform the data
    transform_companies_to_qa_format(csv_path, output_path, sample_size=100)

    print("Transformation completed successfully!")


if __name__ == "__main__":
    main()

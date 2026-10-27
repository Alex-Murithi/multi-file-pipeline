"""
Day 2 - Multi-File Data Processing Pipeline
Squad Python Specialization - Data Engineering

Usage:
python pipeline.py --input data/ --output output/
"""

import csv
import argparse
import logging
from pathlib import Path
from datetime import datetime

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

# ==========================================================
# CONFIGURATION
# ==========================================================

REQUIRED_COLUMNS: set[str] = {
    "transaction_id",
    "date",
    "branch",
    "customer_id",
    "product",
    "quantity",
    "unit_price",
    "payment_method",
}

# Update after inspecting Day 3 file
COLUMN_ALIASES: dict[str, str] = {
    # Example:
    # "product_name": "product"
}


# ==========================================================
# FILE DISCOVERY
# ==========================================================

def discover_files(
    folder: Path,
    pattern: str = "transactions_*.csv"
) -> list[Path]:
    """
    Return transaction files in sorted order.
    """

    files = sorted(folder.glob(pattern))

    logging.info(
        f"Discovered {len(files)} transaction files."
    )

    return files


# ==========================================================
# READ CSV FILES
# ==========================================================

def read_transactions(
    path: Path
) -> tuple[list[str], list[dict]]:
    """
    Read one transaction file.

    Returns:
        header
        rows
    """

    logging.info(f"Reading {path.name}")

    rows = []

    with open(
        path,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        header = reader.fieldnames or []

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            row["source_file"] = path.name
            row["row_number"] = row_number

            rows.append(row)

    logging.info(
        f"{path.name}: {len(rows)} rows loaded."
    )

    return header, rows


# ==========================================================
# COLUMN VALIDATION
# ==========================================================

def validate_columns(
    header: list[str],
    required: set[str] = REQUIRED_COLUMNS
) -> set[str]:
    """
    Return missing required columns.
    """

    mapped_header = {
        COLUMN_ALIASES.get(column, column)
        for column in header
    }

    missing_columns = required - mapped_header

    return missing_columns


# ==========================================================
# ROW VALIDATION
# ==========================================================

def find_problems(
    row: dict,
    seen_ids: set[str]
) -> list[str]:

    reasons = []

    # Missing required values

    for column in REQUIRED_COLUMNS:

        value = str(
            row.get(column, "")
        ).strip()

        if value == "":
            reasons.append(
                f"missing_{column}"
            )

    # Quantity

    try:

        quantity = int(
            str(row.get("quantity", "")).strip()
        )

        if quantity <= 0:
            reasons.append(
                "invalid_quantity"
            )

    except (TypeError, ValueError):
        reasons.append(
            "invalid_quantity"
        )

    # Unit Price

    try:

        price = int(
            str(row.get("unit_price", "")).strip()
        )

        if price <= 0:
            reasons.append(
                "invalid_unit_price"
            )

    except (TypeError, ValueError):
        reasons.append(
            "invalid_unit_price"
        )

    # Duplicate transaction IDs

    transaction_id = str(
        row.get("transaction_id", "")
    ).strip()

    if transaction_id and transaction_id in seen_ids:

        reasons.append(
            "duplicate_transaction_id"
        )

    return reasons


# ==========================================================
# CLEAN ROW
# ==========================================================

def clean_row(row: dict) -> dict:
    """
    Normalise a valid row.
    """

    cleaned = {
        key: value.strip()
        if isinstance(value, str)
        else value
        for key, value in row.items()
    }

    cleaned["quantity"] = int(
        cleaned["quantity"]
    )

    cleaned["unit_price"] = int(
        cleaned["unit_price"]
    )

    cleaned["line_total"] = (
        cleaned["quantity"]
        * cleaned["unit_price"]
    )

    return cleaned


# ==========================================================
# WRITE CSV
# ==========================================================

def write_csv(
    rows: list[dict],
    path: Path,
    fieldnames: list[str]
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in rows:

            writer.writerow(
                {
                    field: row.get(field, "")
                    for field in fieldnames
                }
            )

    logging.info(
        f"Wrote {len(rows)} records to {path.name}"
    )


# ==========================================================
# SUMMARY
# ==========================================================

def build_summary(stats: dict) -> str:

    issue_text = (
        "\n".join(stats["column_issue_details"])
        if stats["column_issue_details"]
        else "None"
    )

    summary = f"""
=== Processing summary ===
Files discovered:         {stats['files_discovered']}
Files processed:          {stats['files_processed']}
Files with column issues: {stats['files_with_column_issues']}

Column details:
{issue_text}

Rows read:                {stats['rows_read']}
Rows accepted:            {stats['rows_accepted']}
Rows rejected:            {stats['rows_rejected']}
  - missing values:       {stats['missing_values']}
  - invalid numbers:      {stats['invalid_numbers']}
  - duplicate IDs:        {stats['duplicate_ids']}

Total revenue (KES):      {stats['total_revenue']}
Run finished at:          {datetime.now().isoformat()}
"""

    return summary.strip()


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def run_pipeline(
    input_dir: Path,
    output_dir: Path
) -> dict:

    logging.info("Pipeline started")

    files = discover_files(input_dir)

    accepted_rows = []
    rejected_rows = []

    seen_ids = set()

    stats = {
        "files_discovered": len(files),
        "files_processed": 0,
        "files_with_column_issues": 0,
        "column_issue_details": [],
        "rows_read": 0,
        "rows_accepted": 0,
        "rows_rejected": 0,
        "missing_values": 0,
        "invalid_numbers": 0,
        "duplicate_ids": 0,
        "total_revenue": 0
    }

    for file in files:

        logging.info(
            f"Processing {file.name}"
        )

        header, rows = read_transactions(file)

        missing_columns = validate_columns(header)

        if missing_columns:

            logging.warning(
                f"{file.name} missing columns: "
                f"{missing_columns}"
            )

            stats["files_with_column_issues"] += 1

            stats["column_issue_details"].append(
                f"{file.name}: missing {', '.join(sorted(missing_columns))}"
            )

            continue

        stats["files_processed"] += 1

        for row in rows:

            stats["rows_read"] += 1

            mapped_row = {
                COLUMN_ALIASES.get(k, k): v
                for k, v in row.items()
            }

            problems = find_problems(
                mapped_row,
                seen_ids
            )

            if problems:

                logging.warning(
                    f"Rejected transaction "
                    f"{mapped_row.get('transaction_id','UNKNOWN')}: "
                    f"{'; '.join(problems)}"
                )

                if any(
                    reason.startswith("missing_")
                    for reason in problems
                ):
                    stats["missing_values"] += 1

                if any(
                    "invalid" in reason
                    for reason in problems
                ):
                    stats["invalid_numbers"] += 1

                if (
                    "duplicate_transaction_id"
                    in problems
                ):
                    stats["duplicate_ids"] += 1

                rejected_rows.append({
                    "source_file":
                        mapped_row.get(
                            "source_file"
                        ),
                    "row_number":
                        mapped_row.get(
                            "row_number"
                        ),
                    "transaction_id":
                        mapped_row.get(
                            "transaction_id",
                            ""
                        ),
                    "reasons":
                        "; ".join(problems),
                    **mapped_row
                })

                stats["rows_rejected"] += 1

            else:

                cleaned = clean_row(
                    mapped_row
                )

                accepted_rows.append(
                    cleaned
                )

                stats["rows_accepted"] += 1

                stats["total_revenue"] += (
                    cleaned["line_total"]
                )

                seen_ids.add(
                    cleaned["transaction_id"]
                )

    # ======================================================
    # CONSOLIDATED OUTPUT
    # ======================================================

    consolidated_fields = [
        "transaction_id",
        "date",
        "branch",
        "customer_id",
        "product",
        "quantity",
        "unit_price",
        "line_total",
        "payment_method",
        "payment_ref",
        "source_file"
    ]

    write_csv(
        accepted_rows,
        output_dir /
        "consolidated_transactions.csv",
        consolidated_fields
    )

    # ======================================================
    # REJECTED OUTPUT
    # ======================================================

    if rejected_rows:

        rejected_fields = list(
            rejected_rows[0].keys()
        )

        write_csv(
            rejected_rows,
            output_dir /
            "rejected_transactions.csv",
            rejected_fields
        )

    # ======================================================
    # SUMMARY
    # ======================================================

    summary = build_summary(stats)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    summary_path = (
        output_dir /
        "summary.txt"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(summary)

    logging.info(
        f"Summary written to {summary_path}"
    )

    logging.info(
        f"Accepted Rows: {stats['rows_accepted']}"
    )

    logging.info(
        f"Rejected Rows: {stats['rows_rejected']}"
    )

    logging.info(
        f"Revenue: KES {stats['total_revenue']}"
    )

    logging.info(
        "Pipeline completed successfully."
    )

    return stats


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Multi-file transaction data pipeline"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input data folder"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output folder"
    )

    args = parser.parse_args()

    stats = run_pipeline(
        Path(args.input),
        Path(args.output)
    )

    print()
    print(build_summary(stats))
"""
Project Profit & Loss Tracker
Compatible with Python 3.15.2 (uses only the standard library).

Run in IDLE:
1. Save this file as project_profit_loss.py
2. Open it in IDLE and press F5 (Run > Run Module)

Tax note:
- Tax is modeled as a user-entered estimated percentage applied to taxable profit.
- This is a planning estimate, not tax advice or a tax return.
- "Lost revenue due to taxation" is calculated as estimated tax on profit; tax is not technically lost revenue, so the report labels it separately.
"""

from datetime import datetime
import json
from pathlib import Path

SAVE_FILE = Path("project_profit_loss_jobs.json")


def ask_text(prompt, default=""):
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_float(prompt, default=0.0, minimum=None, maximum=None):
    while True:
        raw = input(f"{prompt} [{default:.2f}]: ").strip()
        if not raw:
            value = default
        else:
            try:
                value = float(raw.replace(",", "").replace("$", "").replace("%", ""))
            except ValueError:
                print("Please enter a number (for example, 1250.00).")
                continue
        if value < 0:
            print("Please enter zero or a positive number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Please enter at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Please enter no more than {maximum}.")
            continue
        return value


def ask_date(prompt, default=""):
    while True:
        value = ask_text(f"{prompt} (YYYY-MM-DD)", default)
        if not value:
            return ""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use the date format YYYY-MM-DD, such as 2026-10-27.")


def money(value):
    return f"${value:,.2f}"


def load_jobs():
    if not SAVE_FILE.exists():
        return []
    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        print("Warning: saved job data could not be read; starting with an empty list.")
        return []


def save_jobs(jobs):
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as file:
            json.dump(jobs, file, indent=2)
        print(f"Saved to: {SAVE_FILE.resolve()}")
    except OSError as exc:
        print(f"Could not save data: {exc}")


def create_job():
    print("\n=== NEW PROJECT / JOB ===")
    job = {
        "job_id": datetime.now().strftime("JOB-%Y%m%d-%H%M%S"),
        "job_name": ask_text("Job / project name"),
        "client": ask_text("Client name and/or business"),
        "location": ask_text("Job location / site address"),
        "description": ask_text("Job details / scope of work"),
        "projection_start": ask_date("Projected start date"),
        "projection_end": ask_date("Projected completion date"),
        "projection_hours": ask_float("Projected total labor hours", 0.0),
        "projected_revenue": ask_float("Expected total revenue / contract price", 0.0),
        "actual_revenue": ask_float("Actual revenue received or earned", 0.0),
        "materials": ask_float("Materials cost", 0.0),
        "rental_equipment": ask_float("Rental equipment cost", 0.0),
        "manpower": ask_float("Manpower / wages / subcontract labor cost", 0.0),
        "other_labor_costs": ask_float("Other labor-related costs", 0.0),
        "other_expenses": ask_float("Other project expenses", 0.0),
        "tax_rate": ask_float("Estimated tax rate (%)", 0.0, minimum=0.0, maximum=100.0),
        "taxable_profit_adjustment": ask_float(
            "Taxable-profit adjustment (deductions enter as positive amount)", 0.0
        ),
        "notes": ask_text("Notes (optional)"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    job["total_cost"] = (
        job["materials"] + job["rental_equipment"] + job["manpower"]
        + job["other_labor_costs"] + job["other_expenses"]
    )
    job["pretax_profit"] = job["actual_revenue"] - job["total_cost"]
    estimated_taxable_profit = max(
        0.0, job["pretax_profit"] - job["taxable_profit_adjustment"]
    )
    job["estimated_tax"] = estimated_taxable_profit * job["tax_rate"] / 100.0
    job["after_tax_profit"] = job["pretax_profit"] - job["estimated_tax"]
    job["profit_margin_percent"] = (
        job["pretax_profit"] / job["actual_revenue"] * 100.0
        if job["actual_revenue"] else 0.0
    )
    job["projected_variance"] = job["actual_revenue"] - job["projected_revenue"]
    return job


def print_job(job):
    print("\n" + "=" * 64)
    print(f"PROJECT PROFIT & LOSS — {job.get('job_name', 'Unnamed job')}")
    print("=" * 64)
    print(f"Job ID:                 {job.get('job_id', '')}")
    print(f"Client / business:      {job.get('client', '')}")
    print(f"Location:               {job.get('location', '')}")
    print(f"Job details:            {job.get('description', '')}")
    print(f"Projected start:         {job.get('projection_start', '') or 'Not set'}")
    print(f"Projected completion:   {job.get('projection_end', '') or 'Not set'}")
    print(f"Projected labor hours:  {job.get('projection_hours', 0):,.2f}")
    print("-" * 64)
    print(f"Projected revenue:      {money(job.get('projected_revenue', 0))}")
    print(f"Actual revenue:         {money(job.get('actual_revenue', 0))}")
    print(f"Revenue vs. projection: {money(job.get('projected_variance', 0))}")
    print("-" * 64)
    print("COST BREAKDOWN")
    print(f"Materials:              {money(job.get('materials', 0))}")
    print(f"Rental equipment:       {money(job.get('rental_equipment', 0))}")
    print(f"Manpower / wages:       {money(job.get('manpower', 0))}")
    print(f"Other labor costs:      {money(job.get('other_labor_costs', 0))}")
    print(f"Other expenses:         {money(job.get('other_expenses', 0))}")
    print(f"TOTAL PROJECT COST:     {money(job.get('total_cost', 0))}")
    print("-" * 64)
    print(f"PRE-TAX PROFIT / LOSS:  {money(job.get('pretax_profit', 0))}")
    print(f"Estimated tax rate:     {job.get('tax_rate', 0):.2f}%")
    print(f"Estimated tax amount:   {money(job.get('estimated_tax', 0))}")
    print(f"AFTER-TAX PROFIT / LOSS:{money(job.get('after_tax_profit', 0))}")
    print(f"Pre-tax profit margin:  {job.get('profit_margin_percent', 0):.2f}%")
    print("-" * 64)
    print("Tax is an estimate based on the entered rate and taxable-profit adjustment.")
    if job.get("notes"):
        print(f"Notes: {job['notes']}")
    print("=" * 64)


def edit_job(job):
    """Edit an existing job; pressing Enter keeps the current value."""
    print("\n=== EDIT PROJECT / JOB ===")
    print("Press Enter to keep the current value for any field.")
    for key, prompt in [
        ("job_name", "Job / project name"),
        ("client", "Clinet name and/or business"),
        ("location", "Job location / site address"),
        ("description", "Job details / scope of work"),
    ]:
        job[key] = ask_text(prompt, str(job.get(key, "")))

    for key, prompt in [("projection_start", "Projected start date"), ("projection_end", "Projected completion date")]:
        current = job.get(key, "")
        while True:
            raw = input(f"{prompt} (YYYY-MM-DD) [{current or 'not set'}] (Enter keeps current; type CLEAR to remove): ").strip()
            if not raw:
                break
            if raw.upper() == "CLEAR":
                job[key] = ""
                break
            try:
                datetime.striptime(raw, "%Y-%m-%d")
                job[key] = raw
                break
            except ValueError:
                print("Use YYYY-MM-DD, such as 2026-10-27.")

    numeric_fields = [
        ("projection_hours", "Projected total labor hours", 0.0, None),
        ("projected_revenue", "expected total revenue / contract price", 0.0, None),
        ("actual_revenue", "Actual revenue recieved or earned", 0.0, None),
        ("materials", "Materials cost", 0.0, None),
        ("rental_equipment", "Rental equipment cost", 0.0, None),
        ("manpower", "Manpower / wages / subcontract labor cost", 0.0, None),
        ("other_labor_costs", "Other labor-related costs", 0.0, None),
        ("other_expenses", "Other project expenses", 0.0, None),
        ("tax_rate", "Estimated tax rate (%)", 0.0, 100.0),
        ("taxable_profit_adjustmnet", "Taxable-profit adjustment (deductions enter as positive amount)", 0.0, None),
    ]
    for key, prompt, minimum, maximum in numeric_fields:
        current = float(job.get(key, 0.0))
        while True:
            raw = input(f"{prompt} [{current:.2f}] (Enter keeps current): ").strip()
            if not raw:
                break
            try:
                value = float(raw.replace(",", "").replace("$", "").replace("%", ""))
            except ValueError:
                print("Please enter a number, such as 1250.00.")
                continue
            if value < minimum or (maximum is not None and value > maximum):
                print(f"Enter a value between {minimum} and {maximum}." if maximum is not None else f"Enter a value of at least {minimum}.")
                continue
            job[key] = value
            break
    job["notes"] = ask_text("Notes", str(job.get("notes", "")))
    job["total_cost"] = sum(job.get(key, 0.0) for key in ("materials", "rental_equipment", "manpower", "other_labor_costs", "other_expenses"))
    job["pretax_profit"] = job.get("actual_revenue", 0.0) - job["total_cost"]
    taxable_profit = max(0.0, job["pretax_profit"] - job.get("taxable_profit_adjustment", 0.0))
    job["estimated_tax"] = taxable_profit * job.get("tax_rate", 0.0) / 100.0
    job["after_tax_profit"] = job["pretax_profit"] - job["estimated_tax"]
    revenue = job.get("actual_revenue", 0.0)
    job["profit_margin_percent"] = job["pretax_profit"] / revenue * 100.0 if revenue else 0.0
    job["projected_variance"] = job.get("actual_revenue", 0.0) - job.get("projected_revenue", 0.0)
    job["updated_at"] = datetime.now().isoformat(timespec="seconds")
    return job


def list_jobs(jobs):
    if not jobs:
        print("\nNo jobs saved yet.")
        return
    print("\n=== SAVED JOBS ===")
    for index, job in enumerate(jobs, start=1):
        print(
            f"{index}. {job.get('job_name', 'Unnamed')} | "
            f"Client: {job.get('client', 'N/A')} | "
            f"Pre-tax P/L: {money(job.get('pretax_profit', 0))} | "
            f"After-tax P/L: {money(job.get('after_tax_profit', 0))}"
        )


def choose_job(jobs):
    list_jobs(jobs)
    if not jobs:
        return None
    while True:
        raw = input("Enter job number (or 0 to cancel): ").strip()
        try:
            number = int(raw)
        except ValueError:
            print("Enter a whole number.")
            continue
        if number == 0:
            return None
        if 1 <= number <= len(jobs):
            return number - 1
        print("That job number is not in the list.")


def portfolio_summary(jobs):
    if not jobs:
        print("\nNo jobs saved yet.")
        return
    projected = sum(j.get("projected_revenue", 0) for j in jobs)
    revenue = sum(j.get("actual_revenue", 0) for j in jobs)
    costs = sum(j.get("total_cost", 0) for j in jobs)
    pretax = sum(j.get("pretax_profit", 0) for j in jobs)
    taxes = sum(j.get("estimated_tax", 0) for j in jobs)
    aftertax = sum(j.get("after_tax_profit", 0) for j in jobs)
    print("\n=== ALL-JOBS SUMMARY ===")
    print(f"Number of jobs:         {len(jobs)}")
    print(f"Projected revenue:      {money(projected)}")
    print(f"Actual revenue:         {money(revenue)}")
    print(f"Total project costs:    {money(costs)}")
    print(f"Combined pre-tax P/L:   {money(pretax)}")
    print(f"Estimated tax total:    {money(taxes)}")
    print(f"Combined after-tax P/L: {money(aftertax)}")


def export_csv(jobs):
    import csv
    if not jobs:
        print("\nNo jobs to export.")
        return
    filename = ask_text("CSV filename", "project_profit_loss_report.csv")
    fields = [
        "job_id", "job_name", "client", "location", "description",
        "projection_start", "projection_end", "projection_hours",
        "projected_revenue", "actual_revenue", "projected_variance",
        "materials", "rental_equipment", "manpower", "other_labor_costs",
        "other_expenses", "total_cost", "pretax_profit", "tax_rate",
        "taxable_profit_adjustment", "estimated_tax", "after_tax_profit",
        "profit_margin_percent", "notes",
    ]
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(jobs)
        print(f"CSV report exported to: {Path(filename).resolve()}")
    except OSError as exc:
        print(f"Could not export CSV: {exc}")


def main():
    jobs = load_jobs()
    print("PROJECT PROFIT & LOSS TRACKER")
    print("Data is saved locally in project_profit_loss_jobs.json.")
    while True:
        print("\nMENU")
        print("1. Add a new job")
        print("2. View a job report")
        print("3. List all jobs")
        print("4. Show all-jobs summary")
        print("5. Export jobs to CSV")
        print("6. Edit existing job")
        print("7. Delete a job")
        print("8. Save and exit")
        choice = input("Choose 1-8: ").strip()

        if choice == "1":
            job = create_job()
            jobs.append(job)
            save_jobs(jobs)
            print_job(job)
        elif choice == "2":
            index = choose_job(jobs)
            if index is not None:
                print_job(jobs[index])
        elif choice == "3":
            list_jobs(jobs)
        elif choice == "4":
            portfolio_summary(jobs)
        elif choice == "5":
            export_csv(jobs)
        elif choice == "6":
            index = choose_job(jobs)
            if index is not None:
                edit_job(jobs[index])
                save_jobs(jobs)
                print("Job updated successfully.")
                print_job(jobs[index])
        elif choice == "7":
            index = choose_job(jobs)
            if index is not None:
                confirm = input(
                    f"Delete '{jobs[index].get('job_name', 'Unnamed job')}'? Type YES to confirm: "
                ).strip()
                if confirm == "YES":
                    removed = jobs.pop(index)
                    save_jobs(jobs)
                    print(f"Deleted: {removed.get('job_name', 'Unnamed job')}")
                else:
                    print("Deletion cancelled.")
        elif choice == "8":
            save_jobs(jobs)
            print("Goodbye.")
            break
        else:
            print("Please choose a number from 1 to 8.")


if __name__ == "__main__":
    main()

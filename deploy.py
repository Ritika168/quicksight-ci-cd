import boto3
import time
import uuid
import json

# ---------------- CONFIG ----------------
ACCOUNT_ID = "557947230077"
REGION = "us-east-1"

SOURCE_ANALYSIS_ID = "3df1ab83-140b-4dd3-bdf8-dc44c9928f5f"

TEMPLATE_ID = "ritika-template-1"

UNIQUE_ID = str(uuid.uuid4())[:8]
NEW_ANALYSIS_ID = f"ritika-analysis-{UNIQUE_ID}"
DASHBOARD_ID = f"ritika-dashboard-{UNIQUE_ID}"

OLD_DATASET_ID = "f8f0ac7b-8297-482a-a1d1-47e5160e5b54"
NEW_DATASET_ID = "ead466a1-5424-4469-b6f5-3c196e137cb9"

DATASET_PLACEHOLDER = "MyDataSet"

USER_ARN = "arn:aws:quicksight:us-east-1:557947230077:user/default/Ritika"

# ---------------------------------------

qs = boto3.client("quicksight", region_name=REGION)

OLD_DATASET_ARN = f"arn:aws:quicksight:{REGION}:{ACCOUNT_ID}:dataset/{OLD_DATASET_ID}"
NEW_DATASET_ARN = f"arn:aws:quicksight:{REGION}:{ACCOUNT_ID}:dataset/{NEW_DATASET_ID}"

# ---------------- TEMPLATE ----------------

def create_template():
    try:
        qs.describe_template(
            AwsAccountId=ACCOUNT_ID,
            TemplateId=TEMPLATE_ID
        )
        print("Template already exists, skipping...")
        return
    except qs.exceptions.ResourceNotFoundException:
        pass

    print("Creating template...")

    qs.create_template(
        AwsAccountId=ACCOUNT_ID,
        TemplateId=TEMPLATE_ID,
        Name="Ritika Template 3",
        SourceEntity={
            "SourceAnalysis": {
                "Arn": f"arn:aws:quicksight:{REGION}:{ACCOUNT_ID}:analysis/{SOURCE_ANALYSIS_ID}",
                "DataSetReferences": [
                    {
                        "DataSetPlaceholder": DATASET_PLACEHOLDER,
                        "DataSetArn": OLD_DATASET_ARN
                    }
                ]
            }
        }
    )

    while True:
        status = qs.describe_template(
            AwsAccountId=ACCOUNT_ID,
            TemplateId=TEMPLATE_ID
        )["Template"]["Version"]["Status"]

        print("Template Status:", status)

        if status == "CREATION_SUCCESSFUL":
            print("Template ready!")
            break
        elif status == "CREATION_FAILED":
            raise Exception("Template creation failed")

        time.sleep(5)

# ---------------- EXPORT JSON ----------------

def export_template_json():
    print("Exporting template JSON...")

    response = qs.describe_template(
        AwsAccountId=ACCOUNT_ID,
        TemplateId=TEMPLATE_ID
    )

    with open("template.json", "w") as f:
        json.dump(response, f, indent=4, default=str)  # ✅ FIX

    print("Template JSON saved as template.json")
# ---------------- ANALYSIS ----------------

def create_analysis():
    print("Creating analysis:", NEW_ANALYSIS_ID)

    qs.create_analysis(
        AwsAccountId=ACCOUNT_ID,
        AnalysisId=NEW_ANALYSIS_ID,
        Name="Ritika Analysis using jenkins",
        SourceEntity={
            "SourceTemplate": {
                "Arn": f"arn:aws:quicksight:{REGION}:{ACCOUNT_ID}:template/{TEMPLATE_ID}",
                "DataSetReferences": [
                    {
                        "DataSetPlaceholder": DATASET_PLACEHOLDER,
                        "DataSetArn": NEW_DATASET_ARN
                    }
                ]
            }
        }
    )

    time.sleep(5)

def grant_analysis_permissions():
    qs.update_analysis_permissions(
        AwsAccountId=ACCOUNT_ID,
        AnalysisId=NEW_ANALYSIS_ID,
        GrantPermissions=[
            {
                "Principal": USER_ARN,
                "Actions": [
                    "quicksight:DescribeAnalysis",
                    "quicksight:DescribeAnalysisPermissions",
                    "quicksight:UpdateAnalysis",
                    "quicksight:DeleteAnalysis",
                    "quicksight:QueryAnalysis",
                    "quicksight:RestoreAnalysis",
                    "quicksight:UpdateAnalysisPermissions"
                ]
            }
        ]
    )

    print("Analysis permissions granted!")

# ---------------- DASHBOARD ----------------

def create_dashboard():
    print("Creating dashboard:", DASHBOARD_ID)

    qs.create_dashboard(
        AwsAccountId=ACCOUNT_ID,
        DashboardId=DASHBOARD_ID,
        Name="Ritika Dashboard2",
        SourceEntity={
            "SourceTemplate": {
                "Arn": f"arn:aws:quicksight:{REGION}:{ACCOUNT_ID}:template/{TEMPLATE_ID}",
                "DataSetReferences": [
                    {
                        "DataSetPlaceholder": DATASET_PLACEHOLDER,
                        "DataSetArn": NEW_DATASET_ARN
                    }
                ]
            }
        }
    )

def wait_for_dashboard():
    print("Waiting for dashboard...")

    while True:
        try:
            status = qs.describe_dashboard(
                AwsAccountId=ACCOUNT_ID,
                DashboardId=DASHBOARD_ID
            )["Dashboard"]["Version"]["Status"]

            print("Dashboard Status:", status)

            if status == "CREATION_SUCCESSFUL":
                break
            elif status == "CREATION_FAILED":
                raise Exception("Dashboard failed")

        except Exception as e:
            print("Waiting...", str(e))

        time.sleep(5)

def grant_dashboard_permissions():
    qs.update_dashboard_permissions(
        AwsAccountId=ACCOUNT_ID,
        DashboardId=DASHBOARD_ID,
        GrantPermissions=[
            {
                "Principal": USER_ARN,
                "Actions": [
                    "quicksight:DescribeDashboard",
                    "quicksight:QueryDashboard",
                    "quicksight:ListDashboardVersions"
                ]
            }
        ]
    )

    print("Dashboard permissions granted!")

# ---------------- MAIN ----------------

if __name__ == "__main__":

    create_template()
    
    # 🔥 NEW FEATURE
    export_template_json()

    create_analysis()
    grant_analysis_permissions()

    create_dashboard()
    wait_for_dashboard()
    grant_dashboard_permissions()

    print("\nDone! JSON exported + dashboard created.")
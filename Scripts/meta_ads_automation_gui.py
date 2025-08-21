import os, sys, tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError

# Constants
API_VERSION = "v23.0"
ODAX_OBJECTIVES = [
    "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT",
    "OUTCOME_LEADS", "OUTCOME_APP_PROMOTION", "OUTCOME_SALES"
]

# Environment setup
load_dotenv()
APP_ID = os.getenv("FB_APP_ID")
APP_SECRET = os.getenv("FB_APP_SECRET")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")

if not all([APP_ID, APP_SECRET, ACCESS_TOKEN, AD_ACCOUNT_ID]):
    sys.exit("❌ Missing environment variables in .env file")

FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN, api_version=API_VERSION)
account = AdAccount(f"{AD_ACCOUNT_ID}")

def create_campaign():
    try:
        # Validate basic inputs
        campaign_name = v_camp_name.get().strip()
        objective = v_objective.get()
        buying_type = v_buying_type.get()
        
        if not campaign_name:
            raise ValueError("Campaign Name is required")
        
        # ═══════════════════════════════════════════════════════════════
        #  CAMPAIGN CREATION
        # ═══════════════════════════════════════════════════════════════
        
        campaign_params = {
            "name": campaign_name,
            "objective": objective,
            "status": "PAUSED",
            "buying_type": buying_type,
            "special_ad_categories": [] if v_special_cat.get() == "NONE" else [v_special_cat.get()]
        }
        
        # Handle RESERVED vs AUCTION differences
        if buying_type == "RESERVED":
            if objective != "OUTCOME_AWARENESS":
                raise ValueError("RESERVED buying type only works with OUTCOME_AWARENESS objective")
        else:  # AUCTION
            daily_budget_val = v_daily_budget.get().strip()
            lifetime_budget_val = v_lifetime_budget.get().strip()
            
            if daily_budget_val:
                campaign_params["daily_budget"] = int(daily_budget_val)
            if lifetime_budget_val:
                campaign_params["lifetime_budget"] = int(lifetime_budget_val)
                
        print("▶️ Creating campaign...")
        campaign = account.create_campaign(fields=[], params=campaign_params)
        campaign_id = campaign.get_id()
        print(f"✅ Campaign created: {campaign_id}")
        
        # Success message
        success_msg = f"🎉 CAMPAIGN CREATED SUCCESSFULLY!\n\n"
        success_msg += f"Campaign ID: {campaign_id}\n"
        success_msg += f"Name: {campaign_name}\n"
        success_msg += f"Objective: {objective}\n"
        success_msg += f"Buying Type: {buying_type}\n"
        success_msg += f"\n✅ Created in PAUSED status for review"
        
        messagebox.showinfo("Campaign Created", success_msg)
        
    except FacebookRequestError as fb_err:
        # Enhanced error reporting
        error_details = []
        error_details.append(f"🚨 Meta API Error:")
        error_details.append(f"Message: {fb_err.api_error_message()}")
        error_details.append(f"Code: {fb_err.api_error_code()}")
        
        if fb_err.api_error_subcode():
            error_details.append(f"Subcode: {fb_err.api_error_subcode()}")
        
        # Get specific field that caused the error
        blame_fields = fb_err.api_blame_field_specs()
        if blame_fields:
            error_details.append(f"\n🔍 PROBLEM FIELD(S):")
            for field_spec in blame_fields:
                if isinstance(field_spec, list):
                    field_path = " → ".join(field_spec)
                    error_details.append(f"   ❌ {field_path}")
                else:
                    error_details.append(f"   ❌ {field_spec}")
        
        error_details.append(f"\nHTTP Status: {fb_err.http_status()}")
        
        full_error = "\n".join(error_details)
        messagebox.showerror("Meta API Error", full_error)
        print(f"Full API error: {fb_err.body()}")
        
    except ValueError as val_err:
        messagebox.showerror("Input Validation Error", str(val_err))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showerror("Unexpected Error", f"An error occurred: {str(e)}")

#  TKINTER GUI (SCROLLABLE)

root = tk.Tk()
root.title("Meta Campaign Creator v23.0")
root.geometry("580x700")  # Smaller window since we're only creating campaigns

# Create scrollable canvas
canvas = tk.Canvas(root, highlightthickness=0, bg="#f8f9fa")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Main form frame
form_frame = ttk.Frame(canvas, padding=20)
canvas.create_window((0, 0), window=form_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

form_frame.bind("<Configure>", on_frame_configure)

# Mouse wheel scrolling
def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# Header
header_frame = ttk.Frame(form_frame)
header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
ttk.Label(header_frame, text="🚀 Meta Campaign Creator", 
          font=("Arial", 14, "bold")).grid(row=0, column=0)
ttk.Label(header_frame, text=f"API {API_VERSION} - RESERVED/AUCTION Support", 
          font=("Arial", 10), foreground="green").grid(row=1, column=0)

# Campaign Section
camp_frame = ttk.LabelFrame(form_frame, text="📈 Campaign Settings", padding=15)
camp_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

# Campaign variables
v_camp_name = tk.StringVar()
v_objective = tk.StringVar(value="OUTCOME_AWARENESS")
v_buying_type = tk.StringVar(value="AUCTION")
v_special_cat = tk.StringVar(value="NONE")
v_daily_budget = tk.StringVar()
v_lifetime_budget = tk.StringVar()

# Campaign fields
ttk.Label(camp_frame, text="Campaign Name *").grid(row=0, column=0, sticky="w", pady=5)
ttk.Entry(camp_frame, textvariable=v_camp_name, width=45).grid(row=0, column=1, sticky="ew", pady=5)

ttk.Label(camp_frame, text="Objective *").grid(row=1, column=0, sticky="w", pady=5)
ttk.Combobox(camp_frame, textvariable=v_objective, values=ODAX_OBJECTIVES, 
             state="readonly", width=42).grid(row=1, column=1, sticky="ew", pady=5)

ttk.Label(camp_frame, text="Buying Type *").grid(row=2, column=0, sticky="w", pady=5)
ttk.Combobox(camp_frame, textvariable=v_buying_type, values=["AUCTION", "RESERVED"], 
             state="readonly", width=42).grid(row=2, column=1, sticky="ew", pady=5)

ttk.Label(camp_frame, text="Special Ad Category").grid(row=3, column=0, sticky="w", pady=5)
ttk.Combobox(camp_frame, textvariable=v_special_cat, 
             values=["NONE", "HOUSING", "EMPLOYMENT", "CREDIT"], 
             state="readonly", width=42).grid(row=3, column=1, sticky="ew", pady=5)

ttk.Label(camp_frame, text="Daily Budget (cents) - AUCTION only").grid(row=4, column=0, sticky="w", pady=5)
ttk.Entry(camp_frame, textvariable=v_daily_budget, width=45).grid(row=4, column=1, sticky="ew", pady=5)

ttk.Label(camp_frame, text="Lifetime Budget (cents) - AUCTION only").grid(row=5, column=0, sticky="w", pady=5)
ttk.Entry(camp_frame, textvariable=v_lifetime_budget, width=45).grid(row=5, column=1, sticky="ew", pady=5)

# Important note
note_frame = ttk.Frame(form_frame)
note_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
ttk.Label(note_frame, text="⚠️ RESERVED campaigns require OUTCOME_AWARENESS objective", 
          font=("Arial", 9), foreground="red", wraplength=500).grid(row=0, column=0)
ttk.Label(note_frame, text="ℹ️ Ad sets are not created for RESERVED campaigns in this version", 
          font=("Arial", 9), foreground="blue", wraplength=500).grid(row=1, column=0)

# Configure column weights
camp_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(0, weight=1)

# Submit Button
submit_frame = ttk.Frame(form_frame)
submit_frame.grid(row=3, column=0, pady=20)
ttk.Button(submit_frame, text="🚀 Create Campaign", 
           command=create_campaign, width=25).grid(row=0, column=0)

# Footer
footer_frame = ttk.Frame(form_frame)
footer_frame.grid(row=4, column=0, sticky="ew", pady=10)
ttk.Label(footer_frame, text="💡 All campaigns created in PAUSED status for review", 
          font=("Arial", 9), foreground="gray").grid(row=0, column=0)
ttk.Label(footer_frame, text="⭐ Fields marked * are required", 
          font=("Arial", 8), foreground="gray").grid(row=1, column=0)

root.mainloop()
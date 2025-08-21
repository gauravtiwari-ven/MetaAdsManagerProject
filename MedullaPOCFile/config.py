class Config_Data:
   bidsts = ['COST_CAP', 'LOWEST_COST_WITHOUT_CAP', 'LOWEST_COST_WITH_BID_CAP']

   adset_settings = {'OUTCOME_LEADS':
                     {'destination_type':{'ON_AD':{'billing_event':'IMPRESSIONS', 'optimization_goal':'LEAD_GENERATION'},
                                          'PHONE_CALL':{'billing_event':'IMPRESSIONS', 'optimization_goal':'QUALITY_CALL'},
                                          'MESSENGER':{'billing_event':'IMPRESSIONS', 'optimization_goal':'LEAD_GENERATION'},
                                          }}}

   campaign_objectives = {'OUTCOME_LEADS':{'bid_strategy':bidsts,'adset_settings':adset_settings['OUTCOME_LEADS']}, 
                     #    'OUTCOME_ENGAGEMENT':adset_settings['OUTCOME_LEADS'],
                    #    'OUTCOME_TRAFFIC':adset_settings['OUTCOME_LEADS'],
                    #    'OUTCOME_SALES':adset_settings['OUTCOME_LEADS'],
                    #    'OUTCOME_AWARENESS':adset_settings['OUTCOME_LEADS'],
                    #    'OUTCOME_APP_PROMOTION':adset_settings['OUTCOME_LEADS']
                       }
   
   
   campaign_columns = ["account_id","campaign_name", "objective","buy_type","campaign_status","bid_strategy"] # removed: "campaign_budget_type","campaign_budget_amount","campaign_spend_cap"

   adset_columns = ["account_id","campaign_name","objective","buy_type","adset_name","adset_budget_amount","conversion_location","fbpage","frequency_cap","prediction_mode","adset_status","start_date","end_date","country","exclude_states","exclude_cities","age_min","age_max","gender","Advantage Detailed Targeting","interests","narrow_targeting","placement_type","publisher_platforms","facebook_positions","instagram_positions","device"] # removed: "prediction_mode","adset_budget_type","adset_lifetime_spend_cap","adset_daily_spend_cap","custom_audience_id","custom_audience_name","custom_audience_description","custom_audience_retention_days","custom_audience_video_ids","custom_audience_content_type","lookalike_audience_id","lookalike_audience_name","lookalike_audience_description","lookalike_audience_ratio","state","city","pincode","latitude","longitude","radius_(km)","Languages","behaviors"
   
   ad_columns = ["conversion_location","fbpage","ad_name","ad_status","ad_format","link","creative_link","primary_text","headline","description","call_to_action","advantage_plus_creative","standard_enhancements_creative","form_title","form_type","form_prefill_questions","form_followup_url","form_custom_questions","form_custom_multiple_choice","form_intro_headline","form_intro_description(line1)","form_headline","form_intro_description(line2)","form_intro_description(line3)","form_intro_description(line4)","form_intro_description(line5)","ty_page_title","ty_page_website_url","ty_page_button_type","ty_page_body","ty_page_button_text","form_tracking_specs"] # removed: "campaign_name","adset_name","dealer_contact","website","privacy_policy","form_headline","account_id","existing_post_id","placement_type","creative_url_params","instagram_user_id","fb_feed","fb_instream_video","fb_marketplace","fb_video_feeds","fb_story","fb_facebook_reels","fb_search","fb_facebook_reels_overlay","ig_ig_search","ig_stream","ig_explore","ig_explore_home","ig_story","ig_reels","ig_reels_overlay","last_cust","facebook_positions","instagram_positions"

   locales = {'English (UK)':24 , "Hindi": 46, "Marathi": 81}


   update_camp_cols = ["account_id",	"campaign_id"	,"campaign_name"	,'adset_id','adset_name','bid_strategy','bid_amount',"campaign_status"	,"campaign_budget_type"	,"campaign_budget_amount", "campaign_logs", "campaign_spend_cap"]
   update_adset_cols = ["account_id", "campaign_id","campaign_name","adset_id", "adset_name","adset_lifetime_spend_cap","adset_daily_spend_cap", "adset_status","adset_budget_type", "adset_budget_amount", "start_date", "end_date", "bid_strategy", "bid_amount",'custom_audience_id', 'custom_audience_name',	'custom_audience_description', 'custom_audience_retention_days', 'custom_audience_video_ids', 'custom_audience_content_type', 'lookalike_audience_id','lookalike_audience_name', 'lookalike_audience_description','lookalike_audience_ratio', "country", "state", "exclude_states", "city", 'pincode', "latitude","longitude", "radius_(km)", "age_min", "age_max", "gender","Advantage Detailed Targeting","Languages","interests","placement_type","publisher_platforms","facebook_positions","instagram_positions","device","campaign_logs","adset_logs"]
   update_ad_cols = ["dealer_contact","website","privacy_policy","account_id","campaign_id","campaign_name","adset_id","adset_name","ad_id","fbpage","creative_id","form_id","conversion_location","placement_type","ad_name","ad_status","ad_format","existing_post_id","link","advantage_plus_creative", "standard_enhancements_creative","creative_link","form_headline","primary_text","headline","description","call_to_action","form_title","form_prefill_questions","form_followup_url","form_custom_multiple_choice","form_custom_questions","form_intro_headline","form_intro_description(line1)","form_intro_description(line2)","form_intro_description(line3)","form_intro_description(line4)","form_intro_description(line5)","form_tracking_specs","creative_url_params","ty_page_title","ty_page_website_url","ty_page_button_type","ty_page_body","ty_page_button_text", 'instagram_user_id',"fb_feed","fb_instream_video","fb_marketplace","fb_video_feeds","fb_story","fb_facebook_reels","fb_search","fb_facebook_reels_overlay","ig_ig_search","ig_stream","ig_explore","ig_explore_home","ig_story","ig_reels","ig_reels_overlay","last_cust","facebook_positions","instagram_positions", "ad_logs"]





# class Config_Data:
#    bidsts = ['COST_CAP', 'LOWEST_COST_WITHOUT_CAP', 'LOWEST_COST_WITH_BID_CAP']

#    adset_settings = {'OUTCOME_LEADS':
#                      {'destination_type':{'ON_AD':{'billing_event':'IMPRESSIONS', 'optimization_goal':'LEAD_GENERATION'},
#                                           'PHONE_CALL':{'billing_event':'IMPRESSIONS', 'optimization_goal':'QUALITY_CALL'},
#                                           'MESSENGER':{'billing_event':'IMPRESSIONS', 'optimization_goal':'LEAD_GENERATION'},
#                                           }}}

#    campaign_objectives = {'OUTCOME_LEADS':{'bid_strategy':bidsts,'adset_settings':adset_settings['OUTCOME_LEADS']}, 
#                      #    'OUTCOME_ENGAGEMENT':adset_settings['OUTCOME_LEADS'],
#                     #    'OUTCOME_TRAFFIC':adset_settings['OUTCOME_LEADS'],
#                     #    'OUTCOME_SALES':adset_settings['OUTCOME_LEADS'],
#                     #    'OUTCOME_AWARENESS':adset_settings['OUTCOME_LEADS'],
#                     #    'OUTCOME_APP_PROMOTION':adset_settings['OUTCOME_LEADS']
#                        }
   
   
#    campaign_columns = ["account_id","campaign_id","campaign_name", "objective","buy_type","campaign_status","bid_strategy", "campaign_spend_cap", "campaign_logs"]

#    adset_columns = ["account_id","campaign_id","campaign_name",'objective',"buy_type","prediction_mode",'campaign_budget_type',"adset_id","bid_strategy","bid_amount","adset_name","adset_budget_type", "adset_budget_amount","frequency_cap", "adset_lifetime_spend_cap","adset_daily_spend_cap","conversion_location","fbpage",'custom_audience_id', 'custom_audience_name',	'custom_audience_description', 'custom_audience_retention_days', 'custom_audience_video_ids', 'custom_audience_content_type', 'lookalike_audience_id','lookalike_audience_name', 'lookalike_audience_description','lookalike_audience_ratio',"adset_status","start_date","end_date", "country", "state", "exclude_states","city",'pincode',"latitude","longitude","radius_(km)","age_min","age_max","gender","Advantage Detailed Targeting","Languages","interests","placement_type","publisher_platforms","facebook_positions","instagram_positions","device", "adset_logs"]
   
#    ad_columns = ["conversion_location","fbpage","campaign_id","campaign_name","adset_id","adset_name","ad_id","dealer_contact","website","privacy_policy", "form_headline",
#     "account_id","ad_name","ad_status","ad_format","existing_post_id","link","creative_link","primary_text","placement_type","headline","description","call_to_action","advantage_plus_creative", "standard_enhancements_creative","form_title","form_prefill_questions","form_followup_url","form_custom_multiple_choice","form_custom_questions","form_intro_headline","form_intro_description(line1)","form_intro_description(line2)","form_intro_description(line3)","form_intro_description(line4)","form_intro_description(line5)","form_tracking_specs","creative_id","form_id","creative_url_params","ty_page_title","ty_page_website_url","ty_page_button_type","ty_page_body","ty_page_button_text","campaign_id","adset_id","ad_id", 'instagram_user_id',"fb_feed","fb_instream_video","fb_marketplace","fb_video_feeds","fb_story","fb_facebook_reels","fb_search","fb_facebook_reels_overlay","ig_ig_search","ig_stream","ig_explore","ig_explore_home","ig_story","ig_reels","ig_reels_overlay","last_cust","facebook_positions","instagram_positions", "ad_logs"]

#    locales = {'English (UK)':24 , "Hindi": 46, "Marathi": 81}


#    update_camp_cols = ["account_id",	"campaign_id"	,"campaign_name"	,'adset_id','adset_name','bid_strategy','bid_amount',"campaign_status"	,"campaign_budget_type"	,"campaign_budget_amount", "campaign_logs", "campaign_spend_cap"]
#    update_adset_cols = ["account_id", "campaign_id","campaign_name","adset_id", "adset_name","adset_lifetime_spend_cap","adset_daily_spend_cap", "adset_status","adset_budget_type", "adset_budget_amount", "start_date", "end_date", "bid_strategy", "bid_amount",'custom_audience_id', 'custom_audience_name',	'custom_audience_description', 'custom_audience_retention_days', 'custom_audience_video_ids', 'custom_audience_content_type', 'lookalike_audience_id','lookalike_audience_name', 'lookalike_audience_description','lookalike_audience_ratio', "country", "state", "exclude_states", "city", 'pincode', "latitude","longitude", "radius_(km)", "age_min", "age_max", "gender","Advantage Detailed Targeting","Languages","interests","placement_type","publisher_platforms","facebook_positions","instagram_positions","device","campaign_logs","adset_logs"]
#    update_ad_cols = ["dealer_contact","website","privacy_policy","account_id","campaign_id","campaign_name","adset_id","adset_name","ad_id","fbpage","creative_id","form_id","conversion_location","placement_type","ad_name","ad_status","ad_format","existing_post_id","link","advantage_plus_creative", "standard_enhancements_creative","creative_link","form_headline","primary_text","headline","description","call_to_action","form_title","form_prefill_questions","form_followup_url","form_custom_multiple_choice","form_custom_questions","form_intro_headline","form_intro_description(line1)","form_intro_description(line2)","form_intro_description(line3)","form_intro_description(line4)","form_intro_description(line5)","form_tracking_specs","creative_url_params","ty_page_title","ty_page_website_url","ty_page_button_type","ty_page_body","ty_page_button_text", 'instagram_user_id',"fb_feed","fb_instream_video","fb_marketplace","fb_video_feeds","fb_story","fb_facebook_reels","fb_search","fb_facebook_reels_overlay","ig_ig_search","ig_stream","ig_explore","ig_explore_home","ig_story","ig_reels","ig_reels_overlay","last_cust","facebook_positions","instagram_positions", "ad_logs"]



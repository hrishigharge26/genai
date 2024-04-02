from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

## configure gemini pro
genai.configure(api_key=os.getenv('GOOGEL_API_KEY'))

#function to load gemini model & sql query as response
def get_gemini_response(question, prompt, input_columns):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0], question, input_columns])
    return response.text

## MOST IMPORTANT !!!
## create your prompt

prompt = [

    """
    You are expert in Oracle R12 database, Netsuite ERP, you are as good as netsuite functional consultant who holds a post of 
    a solution architect!
    Your experties also extends to converting the English questions into the big fat SQL queries.
    Currently you are working on a accelerator tool for Netsuite, which is focusing on extracting the data form the 
    Oracle R-12 DB as a CSV file(which is phase 1 and the phase 2 is to do the CSV import in Nesuite). 
    Your job is to provide the SQL query, which will give the CSV extract. you take column names as a input and  
    write a SQL query for Oracle R-12 database to get the output data to fill in columns provided as input.
    \n\n Example 1 -below are the column names for a vendor master record in Netsuite, whose columns are as follows.
    columns : [ExternalID	Vendor ID	Individual	Mr./Ms…	First Name	Middle Name	Last Name	Company Name	Job Title	Subsidiary	Phone	Alt. Phone	Fax	Email	Web Address	Enable Online Bill Pay	Category	Home Phone	Mobile Phone	Alt. Email	Comments	Contact	Role	Global Subscription Status	Label	Attention	Addressee	Phone	Address 1	Address 2	City	Province/State	Postal Code/Zip	Country	Default Shipping	Default Billing	Label	Attention	Addressee	Phone	Address 1	Address 2	City	Province/State	Postal Code/Zip	Country	Default Shipping	Default Billing	Account	Legal Name	Default Expense Account	Terms	Credit Limit	Currency	1099 Eligible	Project Resource	Work Calendar	Labor Cost	Tax Reg. number	Tax ID	Opening Balance	Opening Balance Date	Opening Balance Account	Print on Check As	Email Preference	Email Preference	Send Transaction Via Email	Send Transaction Via Fax	Send Transaction Via Print	Inactive	Give Access	Send Notification Email	Password	Confirm Password	Role]
    and your reply or we can say the query should look like as follows :-
    SELECT asa.vendor_id
     , asa.segment1 supp_number 
     , asa.vendor_name
     , 'Prudential Overall Supply' primary_subsidiary
     , asa.end_date_active inactive
	 , assa.vendor_site_code site_name
    -- , hp.party_name addressee
     , assa.address_line1||','||assa.address_line2||','||assa.city||','||assa.state||','||assa.zip||','||assa.country Site_address
	 , billaddr.address_line_1||','||billaddr.TOWN_OR_CITY||','||billaddr.REGION_1||','||billaddr.REGION_2||','||billaddr.POSTAL_CODE||','||billaddr.country  bill_to_address
     --, assa.phone
     , billaddr.bill_to_site_flag
     , shipaddr.ship_to_site_flag
	 , assa.purchasing_site_flag
	 , assa.pay_site_flag
	 , assa.tax_reporting_site_flag
	 , DECODE(assa.MATCH_OPTION,'P','Purchase Order','R','Receipt') Invoice_match_option
	 , assa.ship_via_lookup_code Ship_via
     , NVL(asa.vendor_name_alt,hp.party_name)  legal_name
     , hcpp.phone_area_code||' '||hcpp.phone_number phone
     , hcpf.phone_area_code||' '||hcpf.phone_number fax
     , hcpe.email_address
     , hcpe.email_format
     , at.name terms    
     , asa.num_1099 tax_id
     , asa.type_1099 tax_type
     , NVL(asa.federal_reportable_flag,'N') federal_reportable_flag
     , NVL(asa.state_reportable_flag, 'N') state_reportable_flag
     , 'USD' currency
	 , assa.pay_group_lookup_code Pay_group
	 , assa.payment_method_lookup_code payment_method
	 , (SELECT att.tolerance_name 
		FROM apps.ap_tolerance_templates att
		WHERE att.tolerance_id = assa.tolerance_id) Invoice_tolerance
     , gc_prepay.segment1||'.'||gc_prepay.segment2||'.'||gc_prepay.segment3||'.'||gc_prepay.segment4||'.'||gc_prepay.segment5||'.'||gc_prepay.segment6  prepayment_account
     , gc_liabilityacct.segment1||'.'||gc_liabilityacct.segment2||'.'||gc_liabilityacct.segment3||'.'||gc_liabilityacct.segment4||'.'||gc_liabilityacct.segment5||'.'||gc_liabilityacct.segment6  liability_account
  FROM apps.ap_suppliers asa
     , apps.ap_supplier_sites_all assa
     , apps.hz_parties hp
     , apps.hz_party_sites hps
     , apps.hz_locations hzloc
     , apps.hr_locations billaddr
     , apps.hr_locations shipaddr
     , apps.hz_contact_points hcpp
     , apps.hz_contact_points hcpf
     , apps.hz_contact_points hcpe 
     , apps.ap_terms at
     , apps.gl_code_combinations gc_prepay
     , apps.gl_code_combinations gc_liabilityacct
WHERE asa.vendor_id = assa.vendor_id
  AND asa.party_id = hp.party_id
  AND hp.party_id = hps.party_id
  and assa.location_id = hps.location_id
  AND assa.party_site_id = hps.party_site_id
  AND hps.location_id = hzloc.location_id
  AND assa.bill_to_location_id = billaddr.location_id(+)
  AND assa.ship_to_location_id = shipaddr.location_id(+)
  AND hps.status = 'A'
  AND NVL(asa.end_date_active, sysdate +1) > sysdate
  AND NVL(assa.inactive_date, sysdate +1) > sysdate
  AND hcpp.owner_table_name(+) = 'HZ_PARTY_SITES' 
  AND hcpp.owner_table_id(+) = hps.party_site_id 
  AND hcpp.phone_line_type(+) = 'GEN' 
  AND hcpp.contact_point_type(+) = 'PHONE' 
  AND hcpp.primary_flag(+)='Y'
  AND hcpe.owner_table_name(+) = 'HZ_PARTY_SITES' 
  AND hcpe.owner_table_id(+) = hps.party_site_id 
  AND hcpe.contact_point_type(+) = 'EMAIL' 
  AND hcpe.primary_flag(+)='Y' 
  AND hcpf.owner_table_name(+) = 'HZ_PARTY_SITES'
  AND hcpf.owner_table_id(+) = hps.party_site_id
  AND hcpf.phone_line_type(+) = 'FAX'         
  AND hcpf.contact_point_type(+) = 'PHONE'
  AND asa.terms_id = at.term_id
  AND gc_prepay.code_combination_id(+)=assa.prepay_code_combination_id
  AND gc_liabilityacct.code_combination_id(+)=assa.accts_pay_code_combination_id
  AND TO_DATE(asa.last_update_date, 'dd-mm-yyyy') BETWEEN TO_DATE(sysdate-1750,'dd-mm-yyyy') AND TO_DATE(sysdate,'dd-mm-yyyy')
 --AND asa.vendor_id = 1640
 --AND assa.MATCH_OPTION = 'R'
  ORDER BY asa.last_update_date DESC;
  \n\n Please note that, there might be a case that in R-12 that column might be empty so in the query also you will just give the column that is empty.
  and all the columns in output query should have the same name as given in input tag. 

    """
]

## Create your streamlit app

st.set_page_config(page_title="I can write any sql query")
st.header("TEXT to SQL app")

question = st.text_input('Input: ',key='input')
input_columns = st.text_input('Column Names', key= 'colnames')

submit = st.button("ask the question")

if submit:
    response=get_gemini_response(question,prompt, input_columns)
    print(response)
    st.write('your SQL query is',response)
    

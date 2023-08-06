from trexmodel.models.datastore.pos_models import InvoiceNoGeneration,\
    RoundingSetup, DinningOption, PosPaymentMethod
from trexmodel.models.datastore.merchant_models import ReceiptSetup

def construct_setting_by_outlet(outlet, device_setting=None):


    merchant_acct           = outlet.merchant_acct_entity
    invoice_no_generation   = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
    rounding_setup          = RoundingSetup.get_by_merchant_acct(merchant_acct)
    receipt_setup           = ReceiptSetup.get_by_merchant_acct(merchant_acct)
    dinning_option_json     = []
    dinning_option_list     = DinningOption.list_by_merchant_acct(merchant_acct)
    
    account_settings        = {
                                'account_code'  : merchant_acct.account_code,
                                'currency'      : merchant_acct.currency_code,
                                'locale'        : merchant_acct.locale,    
                                }
    
    if dinning_option_list:
        for d in dinning_option_list:
            dinning_option_json.append({
                                        'option_key'                : d.key_in_str,
                                        'option_name'               : d.name,
                                        'option_prefix'             : d.prefix,
                                        'is_default'                : d.is_default,
                                        'is_dinning_input'          : d.is_dinning_input,
                                        'is_delivery_input'         : d.is_delivery_input,
                                        'is_takeaway_input'         : d.is_takeaway_input,
                                        'is_self_order_input'       : d.is_self_order_input,
                                        'is_self_payment_mandatory' : d.is_self_payment_mandatory,
                                        'dinning_table_is_required' : d.dinning_table_is_required,
                                        'assign_queue'              : d.assign_queue,
                                        })
    
    
    account_settings['dinning_option_list'] = dinning_option_json
    if invoice_no_generation:
        account_settings['invoice_settings']    = {
                                                     'invoice_no_generators'    : invoice_no_generation.generators_list,
                                                                     
                                                    }
    else:
        account_settings['invoice_settings'] = {}
    
    if receipt_setup:
        account_settings['receipt_settings'] = {
                                                'header_data_list': receipt_setup.receipt_header_settings,
                                                'footer_data_list': receipt_setup.receipt_footer_settings or [],
                                                }
    
    if rounding_setup:
        account_settings['rounding_settings']     = {
                                                    'rounding_interval' : rounding_setup.rounding_interval,
                                                    'rounding_rule'     : rounding_setup.rounding_rule,
                                                    }
    pos_payment_method_json = []
    pos_payment_method_list = PosPaymentMethod.list_by_merchant_acct(merchant_acct)
    
    if pos_payment_method_list:
        for d in pos_payment_method_list:
            pos_payment_method_json.append({
                                        'code'                  : d.code,
                                        'key'                   : d.key_in_str,
                                        'label'                 : d.label,
                                        'is_default'            : d.is_default,
                                        'is_rounding_required'  : d.is_rounding_required,
                                        })
    
    account_settings['assigned_service_charge_setup']   = outlet.service_charge_settings
    account_settings['assigned_tax_setup']              = outlet.assigned_tax_setup
    account_settings['dinning_table_list']              = outlet.assigned_dinning_table_list
    account_settings['show_dinning_table_occupied']     = outlet.show_dinning_table_occupied
    account_settings['payment_methods']                 = pos_payment_method_json
    
    
    outlet_details = {
                    'key'                        : outlet.key_in_str,
                    'id'                         : outlet.id,
                    'outlet_name'                : outlet.name,
                    'company_name'               : outlet.company_name,
                    'brand_name'                 : merchant_acct.brand_name,
                    'business_reg_no'            : outlet.business_reg_no,
                    'address'                    : outlet.address,
                    'email'                      : outlet.email,
                    'phone'                      : outlet.office_phone,
                    'website'                    : merchant_acct.website or '',  
                        
                    }
    
    program_configurations = {
                            'prepaid_configuration' : merchant_acct.prepaid_configuration,
                            'days_of_return_policy' : merchant_acct.program_settings.get('days_of_return_policy'),
                            }
    
    setting =  {
                'company_name'                      : merchant_acct.company_name,
                'website'                           : merchant_acct.website,
                'account_id'                        : merchant_acct.key_in_str,
                'api_key'                           : merchant_acct.api_key,
                'logo_image_url'                    : merchant_acct.logo_public_url,
                'account_settings'                  : account_settings,
                'outlet_details'                    : outlet_details,
                'program_configurations'            : program_configurations,
                'membership_configurations'         : merchant_acct.membership_configuration, 
                } 
    if device_setting:
        setting['activation_code']  = device_setting.activation_code
        setting['device_name']      = device_setting.device_name
        setting['device_id']        = device_setting.device_id
        
    return setting
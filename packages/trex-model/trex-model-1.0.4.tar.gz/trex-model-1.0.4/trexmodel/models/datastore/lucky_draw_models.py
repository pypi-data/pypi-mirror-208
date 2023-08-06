'''
Created on 12 May 2023

@author: jacklok
'''
import logging
from trexmodel import program_conf
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import MerchantUser
from trexlib.utils.string_util import is_not_empty

logger = logging.getLogger('model')

class LuckyDrawBase(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    start_date              = ndb.DateProperty(required=True)
    end_date                = ndb.DateProperty(required=True)
    archived                = ndb.BooleanProperty(default=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)
    
class InstantLuckyDraw(LuckyDrawBase):
    
    requirement_settings    = ndb.JsonProperty(required=True)
    prize_settings          = ndb.JsonProperty(required=True)
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None, start_date=None, end_date=None, requirement_settings={}, prize_settings={}, 
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        instant_lucky_draw = InstantLuckyDraw(
                                parent                  = merchant_acct.create_ndb_key(),
                                label                   = label,
                                desc                    = desc,
                                start_date              = start_date,
                                end_date                = end_date,
                                requirement_settings    = requirement_settings,
                                prize_settings          = prize_settings,
                                created_by              = created_by.create_ndb_key(),
                                created_by_username     = created_by_username,
                                )
        instant_lucky_draw.put()
        
    @staticmethod
    def update(instant_lucky_draw, label=None, desc=None, start_date=None, end_date=None, requirement_settings={}, prize_settings={}, 
               modified_by=None):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        instant_lucky_draw.label                = label
        instant_lucky_draw.desc                 = desc
        instant_lucky_draw.start_date           = start_date
        instant_lucky_draw.end_date             = end_date
        instant_lucky_draw.requirement_settings = requirement_settings
        instant_lucky_draw.prize_settings       = prize_settings
        
        instant_lucky_draw.modified_by = modified_by.create_ndb_key()
        instant_lucky_draw.modified_by_username = modified_by_username
                
        
        instant_lucky_draw.put()    

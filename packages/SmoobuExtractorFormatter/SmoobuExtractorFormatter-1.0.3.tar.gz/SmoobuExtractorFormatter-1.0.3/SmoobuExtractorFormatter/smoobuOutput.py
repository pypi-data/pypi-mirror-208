import os
import pandas as pd
import numpy as np

name_menage = "frais_menage"
name_taxe = "taxe_sejour"

TAB_INITIAL = {
	"type": "type",

	"created-at": "created-at",

	"modifiedAt": "modifiedAt",

	"channel": "channel",

	"guest-name": "guest-name",

	"firstname": "firstname",

	"lastname": "lastname",

	"email": "email",

	"phone": "phone",

	"adults": "adults",

	"children": "children",

	"check-in": "check-in",

	"check-out": "check-out",

	"price": "total-price",

	"commission-included": "commission-included",

	"guest-app-url": "guest-app-url",

	"is-blocked-booking": "is-blocked-booking",

	"guestId": "guest_id",

	"apartment_id": "apartment_id",

	"apartment_name": "apartment-name",

	"plateforme_id": "plateforme_id",

	"plateforme_name": "plateforme-name",

	"client": "client",

	"statut": "statut",

	"nuits": "nuits",

	"reservation-id": "reservation-id",

	"reservation-num": "reservation-num",

	"created_at": "created_at",

	"modified_at": "modified_at",

	"basePrice": "basePrice",

	"Commission <-> commission": "commission",

	"frais de ménage <-> channelCustom": name_menage,

	"taxe de séjour <-> channelCustom": name_taxe,

	"Cleaning fee <-> cleaningFee": name_menage,

	"Airbnb Collected Tax <-> channelCustom": name_taxe,

	"supplément serviettes <-> channelCustom": "supp_serviettes",

	"TVA <-> channelCustom": "TVA",

	"frais de linge de lit <-> channelCustom": "frais_linge_lit",

	"Frais de nettoyage <-> cleaningFee": name_menage,

	"Taxe de séjour <-> addon": name_taxe,

	"[Sejournez à Troyes] Frais de gestion <-> addon": "frais_gestion", # à voir

	"Total Paid Amount <-> channelCustom": "Total", # à voir

	"PASS_THROUGH_PET_FEE <-> channelCustom": "supp_animaux",

	"frais de consommation d'électricité <-> channelCustom": "frais_electricite",

	"frais d'entretien ménager <-> channelCustom": name_menage
}




class SmoobuOutput:
    
    """
    Changes the format of the excel (or the json) given by the scrapping tool
    of the Smoobu application 
    
    :param file: the excel file or the json file to be changed
    :type file: str
    
    :param table: the table of the columns/keys to be changed
    :type table: dict

    """
    
    def __init__(self,file):
        self.file = file
        
        
    def format_allBookings(self,path_output = "./",table = TAB_INITIAL):
        
        def len_value(x):
            return len(x)

        def one_value(x):
            if len(x) == 1:
                return x[0]
            else:
                return x
        
        
        file_name,file_extension = os.path.splitext(self.file)
    

        if(file_extension == ".xlsx"):
            
            bookings = pd.read_excel(self.file)
            bookings.rename(columns = table, inplace = True)
            
            number_menage = bookings['frais_menage'].shape[0]
            number_sejour = bookings['taxe_sejour'].shape[0]
            
            
            
            
            # merging every columns into one : frais de menage
            
            bookings['frais_menage_'] = bookings['frais_menage'].apply(lambda x: [val for val in x if pd.notna(val)], axis=1)
            

            lens = bookings['frais_menage_'].apply(len_value)
            
            if lens[lens == 2].shape[0] == 0:
            
                del bookings['frais_menage']
                bookings['frais_menage_'] = bookings['frais_menage_'].apply(one_value)
                bookings['frais_menage_' ] = bookings['frais_menage_'].explode()
                
            else :
                del bookings['frais_menage_']
                
                
                
            # merging every columns into one : taxe de sejour
            
            bookings['taxe_sejour_'] = bookings['taxe_sejour'].apply(lambda x: [val for val in x if pd.notna(val)], axis=1)
            
            lens2 = bookings['taxe_sejour_'].apply(len_value)
            
            if lens2[lens2 == 2].shape[0] == 0:
                del bookings['taxe_sejour']
                bookings['taxe_sejour_'] = bookings['taxe_sejour_'].apply(one_value)
                bookings['taxe_sejour_'] = bookings['taxe_sejour_'].explode()
            else :
                del bookings['taxe_sejour_']
                

            # sum of all the fees into the cleaning fee 
            
            
            bookings['frais_menage_'] = bookings['frais_menage_'].fillna(0.0) 
            bookings['frais_linge_serviettes'] = bookings['frais_linge_lit'].fillna(0.0)   + bookings['supp_serviettes'].fillna(0.0)
            
            
            bookings['frais_menage_'].replace(0,np.nan,inplace = True)
            

            del bookings['frais_linge_lit']
            del bookings['supp_serviettes']
            del bookings['supp_animaux'] # pas compris dans le prix 

            
            
            # new column
            
            bookings['payé-voyageur_calculated'] = bookings['basePrice'].fillna(0.0) + bookings['frais_menage_'].fillna(0.0) + bookings['taxe_sejour_'].fillna(0.0) + bookings['frais_gestion'].fillna(0.0) + bookings['frais_electricite'].fillna(0.0) +   bookings['frais_linge_serviettes'].fillna(0.0)

            

            
            bookings['delta'] = (abs(bookings['total-price'] - bookings['payé-voyageur_calculated']))
            
            bookings = bookings.round(2) # pour eviter des erreurs d'arrondis
            
            bookings['Added-Taxes'] = np.where(bookings['taxe_sejour_'] == bookings['delta'],True,False)
            bookings['Equals-Prices'] = np.where(bookings['total-price'] == bookings['payé-voyageur_calculated'],True,False)
    
                        
            del bookings['delta']

            # newly formated data to excel
            bookings = bookings.round(2)
            bookings.to_excel( path_output +"/Smoobu_"+file_name.split("/")[-1] + ".xlsx", index = False)
            
            print("\nSmoobu file created \n")
            for file in os.listdir():
                if file == "Smoobu_"+file_name.split("/")[-1] + ".xlsx":
                    file_path = os.path.join(os.getcwd(), file)
                    print("File path:", file_path)
                    break
            return bookings
    
    
        else:
            print("Le fichier n'est pas au format excel")
            return None
        







    
        
        
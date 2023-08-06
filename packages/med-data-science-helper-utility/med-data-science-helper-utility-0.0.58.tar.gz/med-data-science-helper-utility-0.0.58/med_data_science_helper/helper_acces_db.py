# -*- coding: utf-8 -*-
import data_science_helper.helper_general as hg
#import core_helper.helper_general as hg
#hg.set_base_path()

#import src.Prj_Core.core_helper.model.general as g
import json
import pandas as pd
import numpy as np
import os.path as path
from pathlib import Path
import os
import ast
from functools import reduce
#import core_helper.helper_general as hg  
#import core_helper.helper_dataframe as hd
#import core_helper.helper_cache as hc
from datetime import datetime
import data_science_helper.helper_dataframe as hd
import data_science_helper.helper_cache as hc
import med_data_science_helper.helper_common as hco
import data_science_helper.helper_output as ho
import data_science_helper.helper_cache as hch
from simpledbf import Dbf5



MR_File_Name = "base.txt"

def set_macro_region(filename):
    global MR_File_Name
    MR_File_Name = filename

def get_macro_region(macro):
    global MR_File_Name
    js_mr = hg.get_base_path()+"/config/macro_region/"+MR_File_Name
    with open(js_mr) as json_file:
        data = json.load(json_file)        
        
    if macro not in data: 

        return None
        #raise Exception("No existe la clave [ " + macro + " ] en el archivo: "+MR_File_Name)
    else:  
        
        return data[macro]
    
def get_macro_regiones():
    global MR_File_Name
    js_mr = hg.get_base_path()+"/config/macro_region/"+MR_File_Name
    with open(js_mr) as json_file:
        data = json.load(json_file)    

    return data

def get_path_BD():
    try:
        path_config_file = hg.get_base_path()+"\\config\\config.txt"
        file = open(path_config_file, "r")
        contents = file.read()
        dictionary = ast.literal_eval(contents)
        dictionary["med-data-science-helper"]
    except:
        print("ERROR: Hay problemas en leer el archivo {}".format(path_config_file))
    
    path_file = dictionary["med-data-science-helper"]+"\\src"
    return path_file


def get_path_BD_siagie_procesado():
    path_file =get_path_BD() +"\\01.SIAGIE\\_data_\\procesado"
    return path_file

def get_path_BD_siagie_sin_procesar():
    path_file =get_path_BD() +"\\01.SIAGIE\\_data_\\sin_procesar"
    return path_file



def get_hogar_2017():  
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_hog.dta'  
    
    #df = pd.read_stata(url_,columns=['c5_p10', 'area']) #,columns=['c5_p10', 'anexo',"grupo_L","grupo_M"]
    df = load_large_dta(url_) #,columns=['c5_p10', 'anexo',"grupo_L","grupo_M"]

    return df

def get_poblacion_2017():  
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'  
    
    #df = pd.read_stata(url_,columns=['c5_p10', 'area']) #,columns=['c5_p10', 'anexo',"grupo_L","grupo_M"]
    
    a = ['c5_p10',"c5_p10a", 'area',"c5_p1","c5_p5","c5_p7"]
    b = ["c5_p8_1","c5_p8_2","c5_p8_3","c5_p8_4","c5_p8_5","c5_p8_6"]
    c = ["c5_p9_1","c5_p9_2","c5_p9_3","c5_p9_4","c5_p9_5","c5_p9_6","c5_p9_7"]
    d = ['c5_p11', 'c5_p12',"c5_p13_niv","c5_p24","c5_p28"]
    
    e = ['long_x', 'lat_y',"id_pob_imp_f","id_hog_imp_f","id_viv_imp_f"]
    
    
    cols = a + b + c + d + e
    
    df = load_large_dta2(url_,cols) #,columns=['c5_p10', 'anexo',"grupo_L","grupo_M"]

    return df


def generate_otros_poblacion_2017():  
    
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'  
    
    url_out = get_path_BD()+'\\14.Hogar_Vivienda\\otros_poblacion_2017_{}.csv'  
        
    cols = ['c5_p10',"area","c5_p1","c5_p11","c5_p12","c5_p13_niv","c5_p24","c5_p28"]
    
    procesar_data_phv(url_,url_out,cols)



def generate_discapacidad_poblacion_2017():  
    
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'  
    
    url_out = get_path_BD()+'\\14.Hogar_Vivienda\\discapacidad_poblacion_2017_{}.csv'  
    
    
    cols = ['c5_p10',"c5_p9_1","c5_p9_2","c5_p9_3","c5_p9_4","c5_p9_5","c5_p9_6","c5_p9_7"]
    
    procesar_data_phv(url_,url_out,cols)

def generate_afiliacion_salud_poblacion_2017():  
    
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'  
    
    url_out = get_path_BD()+'\\14.Hogar_Vivienda\\afiliacion_salud_poblacion_2017_{}.csv'  
    
    
    cols = ['c5_p10',"c5_p8_1","c5_p8_2","c5_p8_3","c5_p8_4","c5_p8_5","c5_p8_6"]
    
    procesar_data_phv(url_,url_out,cols)
    
    
def generate_lat_lon_poblacion_2017():  
    
    url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'  
    
    url_out = get_path_BD()+'\\14.Hogar_Vivienda\\lat_lon_poblacion_2017_{}.csv'  
    
    cols = ['c5_p10','long_x', 'lat_y']
    
    procesar_data_phv(url_,url_out,cols)


def procesar_data_phv(url_origen, url_salida , cols ):  
    
    #url_ = get_path_BD()+'\\14.Hogar_Vivienda\\cpv2017_pob_nominada.dta'      
    #url_out = get_path_BD()+'\\14.Hogar_Vivienda\\afiliacion_salud_poblacion_2017_{}.csv'     
    
    #cols = ['c5_p10',"c5_p8_1","c5_p8_2","c5_p8_3","c5_p8_4","c5_p8_5","c5_p8_6"]
    
    index = load_large_dta2(url_origen,cols,url_salida)
    
    df = pd.DataFrame()
    #index = 30
    for x in range(index):        
        fname = url_salida.format(x)
        df_ = pd.read_csv(fname,sep='|')
        df=df.append(df_)
        
        if(os.path.exists(fname) and os.path.isfile(fname)):
          os.remove(fname)
          print("file deleted")
        
        
        print(x) 
        
    fname = url_salida.format("total")
    print(df.shape)
    df.to_csv(fname, sep='|', encoding='utf-8',index=False)  
    

    #return df

 
    


def load_large_dta2(fname,columns,url_out):
    
    reader=pd.read_stata(fname,chunksize=1000000, columns=columns)
    
    #df = pd.DataFrame()
    index = 0 
    for itm in reader:
        
        if 'c5_p11x' in itm.columns: 
            
            itm['c5_p11'] = itm['c5_p11'].map({'castellano':"CASTE", 
                                               "quechua":"QUECH",    
                                               "awajún / aguaruna":"AW_AG",   
                                               "no sabe / no responde":"NS_NO",   
                                               "wampis":"WAMPI",   
                                               "no escucha, ni habla":"NE_NH", 
                                               "lengua de señas peruanas":"LG_SP",
                                               "aimara":"AIMAR",
                                               "otro lengua extranjera":"OL_EX",
                                               "ashaninka":"ASHAN",
                                               "portugués":"PORTU",
                                               "shipibo - konibo":"SH_KO",
                                               "achuar":"ACHUA",
                                               "shawi/chayahuita":"SH_CH",
                                               "matsigenka/machiguenga":"MA_MA",
                                               
                                               "otra lengua nativa u originaria":"OL_NO",
                                               "kukama kukamiria":"KU_KU",
                                               "ese eja":"ES_EJ",
                                               "nomatsigenga":"NOMAT",
                                               
                                               "jaqaru":"JAQAR",
                                               
                                               "ocaina":"OCAIN",
                                               
                                               "urarina":"URARI",
                                               
                                               "yanesha":"YANES",
                                               "harakbut":"HARAK",
                                               
                                               "kichwa":"KICHWA",
                                               
                                               "kakinte":"KAKIN",
                                               
                                               "sharanahua":"SHARA",
                                               
                                               "tikuna":"TIKUN",
                                               
                                               "cauqui":"CAUQUI",
                                               
                                               "yagua":"YAGUA",
                                               
                                               "murui-muinani":"MU_MU",
                                               
                                               "yaminahua":"YAMIN",
                                               
                                               "cashinahua":"CASHI",
                                               
                                               "secoya":"SECOY",
                                               
                                               "matses":"MATSE",
                                               
                                               "amahuaca":"AMAHU",
                                               "isconahua":"ISCON",
                                            })   
        
        if 'c5_p28x' in itm.columns: 
            
            itm['c5_p28'] = itm['c5_p28'].map({'2 hijos':2, 
                                               "1 hijo":1,    
                                               "3 hijos":3,   
                                               "4 hijos":4,   
                                               "5 hijos":5,   
                                               "6 hijos":6, 
                                               "7 hijos":7,
                                               "8 hijos":8,
                                               "9 hijos":9,
                                               "10 hijos":10,
                                               "11 hijos":11,
                                               "12 hijos":12,
                                               "13 hijos":13,
                                               "14 hijos":14,
                                               "15 hijos":15,
                                               "16 hijos":16,
                                               "17 hijos":17,
                                               "18 hijos":18,
                                               "19 hijos":19,
                                            })   
        
        if 'c5_p24x' in itm.columns: 
            
            itm['c5_p24'] = itm['c5_p24'].map({'soltero/a':"SO", 
                                               "conviviente":"CO",    
                                               "casado/a":"CA",   
                                               "viudo/a":"VI",   
                                               "separado/a":"SE",   
                                               "divorciado/a":"DI",                                             
                                            })   

        if 'c5_p13_nivx' in itm.columns: 
            
            itm['c5_p13_niv'] = itm['c5_p13_niv'].map({'primaria':"PRIM", 
                                                       "secundaria":"SECU",    
                                                       "sin nivel":"SINN",   
                                                       "superior universitaria completa":"SUCO",   
                                                       "inicial":"INIC",   
                                                       "superior no universitaria completa":"SNUC",   
                                                       "superior universitaria incompleta":"SUIM",   
                                                       "superior no universitaria incompleta":"SNUI", 
                                                       "maestría / doctorado":"MADO",
                                                       "básica especial":"BAES",
                                                     })   
        
        if 'c5_p12' in itm.columns: 
            
            itm['c5_p12'] = itm['c5_p12'].map({'si, sabe leer y escribir':1, 
                                               "no, sabe leer y escribir":0                                         
                                             })        
        
        if 'c5_p1X' in itm.columns: 
            
            itm['c5_p1'] = itm['c5_p1'].map({'hijo(a) / hijastro(a)':"hij", 
                                             "jefe o jefa del hogar":"jef",
                                             "esposo(a) / compañero(a)":"esp",
                                             "nieto(a)":"nie",
                                             "otro(a) pariente":"otp",
                                             "hermano(a)":"her",
                                             "otro(a) no pariente":"onp",                                             
                                             "padre / madre / suegro(a)":"pms",
                                             "yerno / nuera":"yen",
                                             "pensionista":"pen",
                                             "trabajador(a) del hogar":"tra",
                                             })

        if 'c5_p8_1' in itm.columns:            
            itm['c5_p8_1'] = np.where(itm['c5_p8_1']=="si, afiliado al sis",1,0)
            
        if 'c5_p9_7' in itm.columns:            
            itm['c5_p9_7'] = np.where(itm['c5_p9_7']=="si tiene alguna discapacidad",1,0)
            
        
        if 'c5_p10' in itm.columns:   
            itm['c5_p10'].replace('', np.nan, inplace=True)
            itm = itm.dropna(subset=['c5_p10'])
            itm['c5_p10'] = itm['c5_p10'].astype(str)
            
        if 'long_x' in itm.columns:   
            itm['long_x'].replace('', np.nan, inplace=True)
            itm = itm.dropna(subset=['long_x'])

        if 'lat_y' in itm.columns:   
            itm['lat_y'].replace('', np.nan, inplace=True)
            itm = itm.dropna(subset=['lat_y'])
        
        #itm = hd.reduce_mem_usage(itm,verbose=True)    
        itm.to_csv(url_out.format(index), sep='|', encoding='utf-8',index=False)  
        print(index)
        #df=df.append(itm)
        #df = hd.reduce_mem_usage(df,verbose=True)
               
        #print(df.shape)       
        #print(df.c5_p8_1.value_counts())
        index += 1
        if index==10:
            break
        
    return index

#df.to_csv("large.csv")


def load_large_dta(fname):
    import sys

    reader = pd.read_stata(fname, columns=['c5_p10', 'area'], iterator=True)
    df = pd.DataFrame()

    try:
        chunk = reader.get_chunk(100*1000)
        while len(chunk) > 0:
            df = df.append(chunk, ignore_index=True)
            chunk = reader.get_chunk(100*100000)
            print('.'),
            sys.stdout.flush()
    except (StopIteration, KeyboardInterrupt):
        pass

    print('\nloaded {} rows').format(len(df))



def get_juntos(anio=2022,cache=False):  
    url_ = get_path_BD()+'\\13.Juntos\\_data_\\Educacion_{}.csv'.format(anio)   
    if anio == 2022:
        df_juntos = pd.read_csv(url_,dtype={'NUMERO_DOCUMENTO':"str"},sep="|")
        df_juntos.rename(columns={"NUMERO_DOCUMENTO": "DNI_MO","TIPO_DOCUMENTO":"TIPODOC_MO"},inplace=True)
    else:
        df_juntos = pd.read_csv(url_,dtype={'DNI_MO':"str"})
     
    df_juntos = df_juntos[df_juntos["TIPODOC_MO"]==1].copy()
    cls = ["TIPODOC_MO","DNI_MO","ANIO","PERIODO","RESULTADO_HOGAR"]   
    return df_juntos[cls]

def get_pivot_juntos(anio=2022,cache=False):

    df = get_juntos(anio=anio, cache=cache)
    
    periodos = df.PERIODO.unique()
    
    df['PERIODO'] = 'VCC_' + df['PERIODO'].astype(str)   
    
    #df_p = df.pivot_table(index=["ID_PERSONA_MO","TIPODOC_MO","DNI_MO","COTEJO_MO","ANIO"], values='RESULTADO_HOGAR', columns='PERIODO') \
      
    
    df_p = df.pivot_table(index=["DNI_MO"], values='RESULTADO_HOGAR', columns='PERIODO', aggfunc=np.max) \
        .reset_index() \
        .rename_axis(None, axis=1)
     
    df_p['JUNTOS'] = 1    
    #df_p.drop(columns=['ID_PERSONA_MO', 'ANIO'], inplace=True)
        
    return df_p , periodos



def get_agg_juntos(anio=2022,cache=False):
        
    df = get_juntos(anio=anio, cache=cache)
    
    df_ = df.groupby(["TIPODOC_MO",'DNI_MO'])[['RESULTADO_HOGAR']].agg('count').reset_index()   
        
    return df_

'''
url_template = get_path_BD()+'\\07.Nexus\\_data_\\{}'     
url_nexus = url_template.format('nexus_2018_2019.xlsb')    
anio = 2019
df_nexus = pd.read_excel(url_nexus, engine='pyxlsb',sheet_name=str(anio))   
print(df_nexus.columns)
print(df_nexus.SITUACION.value_counts()) 

SITUACION
'''
def get_nexus(anio=2020, cache=False):  
    
    filename = f'BD_{anio}.xlsb'
    print(filename)
    
    df_nexus_group = None
    key_cache = hc.get_key_cache(["nexus",anio])
    print(key_cache)
    if cache:
        df_nexus_group = hc.get_cache(filename,key_cache)
        
    if df_nexus_group is not None:
        return df_nexus_group

    
    url_template = get_path_BD()+'\\07.Nexus\\_data_\\{}'     
    url_nexus = url_template.format(filename)    
    print(url_nexus)

    df_nexus = pd.read_excel(url_nexus, dtype={'COD_MOD': str},  engine='pyxlsb',sheet_name="BD_"+str(anio))  

    df_nexus['MODULARIE'] = df_nexus['MODULARIE'].str.strip()
    df_nexus['SITUACION LAB'] = df_nexus['SITUACION LAB'].str.strip()
    df_nexus['ESTPLAZA'] = df_nexus['ESTPLAZA'].str.strip()
    df_nexus['DESCSUBTIPOTRAB'] = df_nexus['DESCSUBTIPOTRAB'].str.strip()
    df_nexus['NIVEL EDUCATIVO'] = df_nexus['NIVEL EDUCATIVO'].str.strip() 

    hch.save_cache(df_nexus,filename,key_cache)  

    return df_nexus

 



def get_ECE_2P(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Primaria\\EM_2019_2P_alumnos.xlsx'  
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,O,Q",dtype={'cod_mod7':str,'anexo':'int8'})    
    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        df["COD_MOD"] =df['COD_MOD'].astype("str")
        df["ANEXO"] =df['ANEXO'].astype("int8")
        return df
    df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
    df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
    df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

    df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
    df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
    df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1

    df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l1',"grupo_l2",'grupo_l3',
                                                 'grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

    df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
    df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "2P"
    
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]


def get_ECE_4P(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Primaria\\EM_2019_4P_alumnos.xlsx'        
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,O,Q",dtype={'cod_mod7':str,'anexo':'int8'})     
        
        df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1
        
        df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l1',"grupo_l2",'grupo_l3',
                                                     'grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

        df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
        df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])
        
    elif  anio == 2018:
        url =   get_path_BD()+'\\06.ECE\\_data_\\ECE 2018\\BD4P.dta'     
        df = pd.read_stata(url,columns=['cod_mod7', 'anexo',"grupo_L","grupo_M"])
        
        df["cod_mod7"] =df['cod_mod7'].astype("str")
        df["anexo"] =df['anexo'].astype("int8")
        
        df.loc[(df['grupo_L'] == "< Nivel 1"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "Nivel 1"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "Nivel 2"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Nivel 3"), 'grupo_l3'] = 1
        
        df.loc[(df['grupo_M'] == "< Nivel 1"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "Nivel 1"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "Nivel 2"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Nivel 3"), 'grupo_m3'] = 1
        
        df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l0','grupo_l1',"grupo_l2",'grupo_l3',
                                                     'grupo_m0','grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

        df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l0']+df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
        df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_l0']+df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])


    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        return df

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "4P"
    df_group.fillna(0,inplace=True)
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]



def get_ECE_2S(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Secundaria\\ECE_2019_2S_alumnos.xlsx'       
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,T,V",dtype={'cod_mod7':str,'anexo':'int8'})    
        
        df.loc[(df['grupo_L'] == "Previo al inicio"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "Previo al inicio"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1

        
    elif  anio == 2018:
        url =   get_path_BD()+'\\06.ECE\\_data_\\ECE 2018\\BD2S.dta'     
        df = pd.read_stata(url,columns=['cod_mod7', 'anexo',"grupo_L","grupo_M"])  
        df["cod_mod7"] =df['cod_mod7'].astype("str")
        df["anexo"] =df['anexo'].astype("int8")
        
        df.loc[(df['grupo_L'] == "< Nivel 1"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "Nivel 1"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "Nivel 2"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Nivel 3"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "< Nivel 1"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "Nivel 1"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "Nivel 2"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Nivel 3"), 'grupo_m3'] = 1
        
    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        return df


    df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l0','grupo_l1',"grupo_l2",'grupo_l3',
                                                 'grupo_m0','grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

    df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l0']+df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
    df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m0']+df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "2S"
    
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]


def get_ECE(anio=2019,cache=False):
    filename = 'ECE'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df
    
    df_2p=get_ECE_2P(anio)
    df_4p=get_ECE_4P(anio)
    df_2_4_p = pd.concat([df_2p,df_4p])
    
    df_2s=get_ECE_2S(anio)    
    df_p = df_2_4_p.groupby(['COD_MOD',"ANEXO"])[['perc_satisf_l',"perc_satisf_m"]].agg("max").reset_index()
    df_2s.drop('grado', axis=1, inplace=True)
    df = pd.concat([df_p,df_2s])
    df["ANEXO"] =df['ANEXO'].astype("int8")
    df["COD_MOD"] =df['COD_MOD'].astype("str") 
    hc.save_cache(df,filename,key_cache)
    
    return df


def get_Censo_Educativo(anio=2019,cache=False):

    filename = 'Evaluacion_Censal'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df

    if anio== 2020:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2020\\Local_lineal.dbf'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2020\\Local_pronoei_1.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P702']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P708']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P712']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P716']=="1") | 
                                                   (df_Local_Lineal['P716']=="2") | 
                                                   (df_Local_Lineal['P716']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P607']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P608']=="1") | 
                                                     (df_Local_Pronoei['P608']=="2") | 
                                                     (df_Local_Pronoei['P608']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
    
    elif anio== 2019:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2019\\Local_Lineal.DBF'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2019\\Local_Pronoei.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P702']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P708']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P711']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P716']=="1") | 
                                                   (df_Local_Lineal['P716']=="2") | 
                                                   (df_Local_Lineal['P716']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P605']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P608']=="1") | 
                                                     (df_Local_Pronoei['P608']=="2") | 
                                                     (df_Local_Pronoei['P608']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
        
    elif anio== 2018:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2018\\pLocal_2018.DBF'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2018\\Localpronoei.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()    
        
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P521']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P506_1']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P506_2']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P506_3']=="1") | 
                                                   (df_Local_Lineal['P506_3']=="2") | 
                                                   (df_Local_Lineal['P506_3']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P607']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P609']=="1") | 
                                                     (df_Local_Pronoei['P609']=="2") | 
                                                     (df_Local_Pronoei['P609']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
    else: 

        return pd.DataFrame(columns =["COD_MOD","ANEXO",'luz','agua','desague'])
        
    df_Local_Pronoei["ANEXO"] =df_Local_Pronoei['ANEXO'].astype("int8")

    dfser = get_df_servicios(anio=anio,columns=['COD_MOD', 'ANEXO', 'CODLOCAL'])
    dfser = pd.merge(dfser,df_Local_Lineal,left_on="CODLOCAL",right_on="CODLOCAL",how="left")
    dfser = pd.merge(dfser,df_Local_Pronoei,left_on=["COD_MOD","ANEXO"],right_on=["COD_MOD","ANEXO"],how="left")

    dfser.loc[(dfser['serv_luz_1'] == 1 )  | (dfser['serv_luz_2'] == 1 ), 'luz'] = 1
    dfser.loc[(dfser['serv_luz_1'] == 0 )  | (dfser['serv_luz_2'] == 0 ), 'luz'] = 0

    dfser.loc[(dfser['serv_agua_1'] == 1 )  | (dfser['serv_agua_2'] == 1 ), 'agua'] = 1
    dfser.loc[(dfser['serv_agua_1'] == 0 )  | (dfser['serv_agua_2'] == 0 ), 'agua'] = 0

    dfser.loc[(dfser['serv_desag_1'] == 1 )  | (dfser['serv_desag_2'] == 1 ), 'desague'] = 1
    dfser.loc[(dfser['serv_desag_1'] == 0 )  | (dfser['serv_desag_2'] == 0 ), 'desague'] = 0
    dfser.drop(columns=['CODLOCAL','serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1','serv_luz_2','serv_agua_2','serv_desag_2'],inplace=True)
    
    dfser["ANEXO"] =dfser['ANEXO'].astype("int8")
    
    hc.save_cache(dfser,filename,key_cache)
    
    return dfser
    



def get_traslados_por_anio(anio,TIPO_TRASLADO='EN EL MISMO AÑO'):
    path_file = get_path_BD_siagie_procesado()
    url_trasl = path_file+'\\Siagie_Traslados_{}.csv'.format(anio)
    sep = "|"
    encoding = 'latin-1'
    cols_tras = ['ID_PERSONA','TIPO_TRASLADO']

    #df_trasl = pd.read_csv(url_trasl ,encoding='utf-8',usecols=cols_tras,  sep=sep,dtype={'PERSONA_NRO_DOC':str})
    df_trasl = pd.read_csv(url_trasl ,encoding=encoding,usecols=cols_tras,  sep=sep,dtype={'ID_PERSONA':int})
    #if(anio==2019):
        #df_trasl = df_trasl[df_trasl.TIPO_TRASLADO==TIPO_TRASLADO].copy()
        #df_trasl.reset_index(drop=True,inplace=True)
 
    df_agg_t  = df_trasl.assign(
     TOTAL_TRASLADOS =   1
    ).groupby(['ID_PERSONA']).agg({'TOTAL_TRASLADOS':'sum'})

    df_agg_t.sort_values(by='TOTAL_TRASLADOS', ascending=False,inplace=True)
    df_agg_t.reset_index(inplace=True)
    
    return df_agg_t



def get_traslados_a_publico(anio,df_servicios=None):
    
    if df_servicios is None:
        df_servicios = get_df_servicios()
    
    path_file = get_path_BD_siagie_procesado()
    url_trasl = path_file+'/Siagie_Traslados_{}.csv'.format(anio)
    sep = "|"
    encoding = 'latin-1'
    cols_tras = ['ID_PERSONA','TIPO_TRASLADO','COD_MOD_ORIGEN','ANEXO_ORIGEN','COD_MOD_DESTINO','ANEXO_DESTINO']

    cl_s = ["COD_MOD","ANEXO","ES_PUBLICO"]
    #df_trasl = pd.read_csv(url_trasl ,encoding='utf-8',usecols=cols_tras,  sep=sep,dtype={'PERSONA_NRO_DOC':str})
    df_trasl = pd.read_csv(url_trasl ,encoding=encoding,usecols=cols_tras,  sep=sep,dtype={'ID_PERSONA':int,
                                                                                           'COD_MOD_ORIGEN':str,
                                                                                           'ANEXO_ORIGEN':int,
                                                                                           'COD_MOD_DESTINO':str,                                                                                           
                                                                                           'ANEXO_DESTINO':int,
                                                                                            })

    df_trasl_origen = pd.merge(df_trasl,df_servicios[cl_s],left_on=["COD_MOD_ORIGEN","ANEXO_ORIGEN"],
                               right_on=["COD_MOD","ANEXO"],how="inner")

    df_trasl_origen.drop(columns=['COD_MOD', 'ANEXO'],inplace=True)
    df_trasl_origen.rename(columns={'ES_PUBLICO': 'ES_PUBLICO_ORIGEN'}, inplace=True)


    df_trasl_destino = pd.merge(df_trasl_origen,df_servicios[cl_s],left_on=["COD_MOD_DESTINO","ANEXO_DESTINO"],
                               right_on=["COD_MOD","ANEXO"],how="inner")

    df_trasl_destino.drop(columns=['COD_MOD', 'ANEXO'],inplace=True)
    df_trasl_destino.rename(columns={'ES_PUBLICO': 'ES_PUBLICO_DESTINO'}, inplace=True)

    df_trasl_destino['TRASLADO_A_PUBLICO'] = np.where((df_trasl_destino.ES_PUBLICO_ORIGEN==0) & 
                                                      (df_trasl_destino.ES_PUBLICO_DESTINO==1),1,0)


    df_trasl_destino = df_trasl_destino[df_trasl_destino["TRASLADO_A_PUBLICO"]==1].copy()
    
    df_agg_t  = df_trasl_destino.assign(
     TOTAL_TRASLADOS =   1
    ).groupby(['ID_PERSONA']).agg({'TOTAL_TRASLADOS':'sum'})

    df_agg_t.sort_values(by='TOTAL_TRASLADOS', ascending=False,inplace=True)
    df_agg_t.reset_index(inplace=True)
    

    return df_agg_t



def get_df_notas(anio):
    
    path_file = get_path_BD_siagie_procesado()
    dtype = {'COD_MOD':str,'ANEXO':np.int8,'NOTA_AREA_REGULAR':np.int8,'DA':str}    
    url_notas = path_file+'\\NOTAS_POR_ALUMNO_{}.csv'.format(anio)
    df_notas = pd.read_csv(url_notas ,encoding='utf-8', dtype=dtype)
    
    return df_notas


def get_df_servicios(macro_region=None,region=None,anio=None,totales=False,geo=False,columns=[],full=False):
    print("Imprimiendo el anio servicio ",anio)
    
    anio_min = 2016
    if (anio is not None and anio<anio_min):        
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web.dbf"        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        print("No existe data de servicios menor que {}".format(anio_min)," se usara una bd referencial")
    
    elif anio is None:
        #print("Extrayendo servicios general")
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web.dbf"        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        
    elif anio<=2020:
        url =   get_path_BD()+"\\03.Servicios\\_data_\\Padron_web_{}.dbf".format(anio)        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        if anio==2016:
            df_codii_dre =  pd.read_csv(get_path_BD() + "\\03.Servicios\\_data_\\CODOOII_D_REGION.csv",dtype={'CODOOII': str})
            df_servicios = pd.merge(df_servicios,df_codii_dre,left_on="CODOOII",right_on="CODOOII",how="inner")
            df_servicios.rename(columns={'D_AREASIG': 'DAREACENSO'}, inplace=True)       
        
    elif anio>=2021:        
                
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web_{}.dbf".format(anio)       
        print(url)
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        df_servicios.columns = map(lambda x: str(x).upper(), df_servicios.columns)
        #url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web_2021.dta"        
        #df_servicios = pd.read_stata(url)   
        #df_servicios.columns = map(lambda x: str(x).upper(), df_servicios.columns)
        
    if full:
        df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        #return df_servicios    

    elif len(columns)>0:
        if "ANEXO" in df_servicios:
            df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        df_servicios =  df_servicios[columns].copy() 
    else:
        
        cls = ["COD_MOD","ANEXO","GESTION","DAREACENSO",'D_TIPSSEXO','D_REGION',"CODGEO"]
        if totales:
            cls = cls + ['TALUM_HOM','TALUM_MUJ','TALUMNO', 'TDOCENTE', 'TSECCION']        
            
        if geo:
            cls = cls + ['CODOOII','NLAT_IE', 'NLONG_IE']
        
        df_servicios = df_servicios[cls].copy() 
        df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        df_servicios["GESTION"] =df_servicios['GESTION'].astype("int8")    
    
        #df_servicios["AREA_CENSO"] =df_servicios['AREA_CENSO'].astype("int8")
        df_servicios['ES_PUBLICO'] = np.where(df_servicios['GESTION'].isin([1,2]),1,0)
        df_servicios['ES_URBANA'] = np.where(df_servicios['DAREACENSO']=='Urbana',1,0)
        df_servicios['ES_MIXTO'] = np.where(df_servicios['D_TIPSSEXO']=='Mixto',1,0)
        df_servicios['COD_MOD']=df_servicios['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
        
        df_servicios.drop(['GESTION', 'DAREACENSO', 'D_TIPSSEXO'], axis=1,inplace=True)
    

    if macro_region is not None  :
        l_mr = get_macro_region(macro_region)
        
        if l_mr is None:
            with ho.pretty_output("\033[1;31m") as out:
                out.write('Advertencia, no se aplicara el filtro de macro region -'+macro_region+"- porque no existe")
        else:           
            df_servicios = df_servicios[df_servicios["D_REGION"].isin(l_mr)].copy()
    
    if region is not None:
        df_servicios = df_servicios[df_servicios["D_REGION"]==region].copy()
        
        
    #eliminando tildes
    cols = df_servicios.select_dtypes(include=[np.object]).columns
    df_servicios[cols] = df_servicios[cols].apply(lambda x: x.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

                
    return df_servicios


def get_desertores_por_anio(anio,modalidad=None):
    
    path_file = get_path_BD_siagie_procesado()
    anios_str=str(anio)+"_"+str(anio+1)
    var_obj_common = f"DESERCION_{anios_str}"
    var_obj_ebr = f"DESERCION_EBR_{anios_str}"
    var_obj_ebe = f"DESERCION_EBE_{anios_str}"

    if modalidad is None:
        
        url_ebr = path_file+"\\DESERCION\\"+var_obj_ebr+".csv"
        ds_ebr = pd.read_csv(url_ebr)    
        ds_ebr.rename(columns={var_obj_ebr:var_obj_common }, inplace=True)
        
        if anio >=2018:
            list_df = []
            list_df.append(ds_ebr)
            
            url_ebe = path_file+"\\DESERCION\\" +var_obj_ebe+".csv"
            ds_ebe = pd.read_csv(url_ebe)
            ds_ebe.rename(columns={var_obj_ebe:var_obj_common }, inplace=True)
            
            list_df.append(ds_ebe)
            ds = pd.concat(list_df)
            return ds
        else:
            return ds_ebr
    else:
        url = path_file+f"\\DESERCION\\DESERCION_{modalidad}_{anios_str}.csv"
        ds = pd.read_csv(url)
        
        if(modalidad=="EBR"):
            ds.rename(columns={var_obj_ebr:var_obj_common }, inplace=True)
        elif(modalidad=="EBE"):
            ds.rename(columns={var_obj_ebe:var_obj_common }, inplace=True)        
           
        
        return ds


def get_shock_economico(anio,cache=False):
    
    filename = 'shock_economico'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df
    
    columns_n = ["ID_PERSONA","LOG_ING_T_MAS_1_IMP_DIST","NA_LOG_ING_T_MAS_1_IMP_DIST"] 
    dtypes_columns={'ID_PERSONA':int}
    
    if anio ==2018:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_EBE_2018_v2.csv"
        ds_ = pd.read_csv(url,usecols=columns_n,dtype=dtypes_columns)
    
    elif anio ==2022:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_EBE_2022_v2.csv"
        ds_ = pd.read_csv(url,usecols=columns_n,dtype=dtypes_columns)

    elif anio ==2023:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_EBE_2023_v2.csv"
        ds_ = pd.read_csv(url,usecols=columns_n,dtype=dtypes_columns)
        
    elif anio ==2020:  
        
        url_ini = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_INI_2020_v2.csv"
        ds_ini =  pd.read_csv(url_ini,usecols=columns_n,dtype=dtypes_columns)
        
        url_ebr = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_2020_v2.csv"
        ds_ebr =  pd.read_csv(url_ebr,usecols=columns_n,dtype=dtypes_columns)    
        
        url_ebe = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBE_2020_v2.csv"
        ds_ebe =  pd.read_csv(url_ebe,usecols=columns_n,dtype=dtypes_columns)    
            
        ds_ = pd.concat([ds_ini, ds_ebr,ds_ebe])       

    else:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_{}_{}_v2.csv".format("EBR",anio) 
        ds_ = pd.read_csv(url,usecols=columns_n,dtype=dtypes_columns)


    if anio ==2020:
        print("ds_ : ",ds_.shape)
        ds_["INGRESO_SIN_LOG"] = np.exp(ds_["LOG_ING_T_MAS_1_IMP_DIST"])
        
        df_siagie_ebr = get_siagie_por_anio(anio,modalidad="EBR",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  
        df_siagie_ebe = get_siagie_por_anio(anio,modalidad="EBE",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  
        
        df_siagie = pd.concat([df_siagie_ebr, df_siagie_ebe])  
        print("df_siagie : ",df_siagie.shape)
        df_serv = get_df_servicios(anio=anio,columns=["COD_MOD","ANEXO","CODGEO"])
        df_merge = pd.merge(df_siagie, df_serv, left_on=["COD_MOD","ANEXO"], right_on=["COD_MOD","ANEXO"],  how='inner')      
        print("df_merge : ",df_merge.shape)
        
        
        df_merge_schok = pd.merge(df_merge, ds_, left_on="ID_PERSONA", right_on="ID_PERSONA",  how='left')
        print("df_merge_schok : ",df_merge_schok.shape)
        
        df_merge_schok['INGRESO_SIN_LOG'] = df_merge_schok['INGRESO_SIN_LOG'].fillna(df_merge_schok.groupby(['ID_NIVEL','CODGEO'])['INGRESO_SIN_LOG'].transform('mean')) 
        df_merge_schok['INGRESO_CON_LOG'] = np.log(df_merge_schok['INGRESO_SIN_LOG'])            
        
        df_merge_schok.loc[(df_merge_schok['LOG_ING_T_MAS_1_IMP_DIST'].isna()), 'LOG_ING_T_MAS_1_IMP_DIST'] = df_merge_schok['INGRESO_CON_LOG']
        df_merge_schok.loc[(df_merge_schok['NA_LOG_ING_T_MAS_1_IMP_DIST'].isna()), 'NA_LOG_ING_T_MAS_1_IMP_DIST'] = 1
    
        df_merge_schok.drop(columns=['ID_NIVEL','COD_MOD','ANEXO','INGRESO_SIN_LOG', 'INGRESO_CON_LOG',"CODGEO"],inplace=True)
        
        hc.save_cache(df_merge_schok,filename,key_cache)
        return df_merge_schok
    else:
        
        hc.save_cache(ds_,filename,key_cache)
        return ds_

def get_sisfoh():
    url_sisfoh = get_path_BD()+'\\04.SISFOH\\_data_\\NOMINAL_SISFOH.csv'
    cols = ['PERSONA_NRO_DOC','SISFOH_CSE']    
    df_sisfoh = pd.read_csv(url_sisfoh ,usecols=cols, encoding='utf-8', dtype={'PERSONA_NRO_DOC':str})
    df_sisfoh.drop_duplicates(subset ="PERSONA_NRO_DOC", keep = "last", inplace = True)
    return df_sisfoh


def get_distancia_prim_sec():
    
    url_ddist = get_path_BD() + "\\03.Servicios\\_data_\\SecundariaCerca.csv"
    df_sec_cerca =pd.read_csv(url_ddist, encoding="utf-8",index_col=0) 

    df_sec_cerca.loc[(df_sec_cerca['Distancia'] == 0), 'GRUPO_DISTANCIA_SEC'] = '0K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 0) & (df_sec_cerca['Distancia'] <= 1000), 'GRUPO_DISTANCIA_SEC'] = 'MENOR_1K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 1000) & (df_sec_cerca['Distancia'] <= 5000), 'GRUPO_DISTANCIA_SEC'] = '1K_5K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 5000), 'GRUPO_DISTANCIA_SEC'] = 'MAYOR_5K'

    df_sec_cerca.columns = [x.upper() for x in df_sec_cerca.columns]
    df_sec_cerca.rename({'DISTANCIA': 'DISTANCIA_SEC'}, axis=1, inplace=True)

    df_sec_cerca[['COD_MOD','ANEXO']] = df_sec_cerca.CODIGOLUGAR.str.split("-",expand=True)
    df_sec_cerca['ANEXO'] = df_sec_cerca['ANEXO'].astype('uint8')

    df_sec_cerca['COD_MOD']=df_sec_cerca['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    del df_sec_cerca['SECUNDARIACERCA']
    del df_sec_cerca['CODIGOLUGAR']
    
    
    return df_sec_cerca



def get_distancia_ini_prim():
    
    url_ddist = get_path_BD() + "\\03.Servicios\\_data_\\PrimariaCerca.csv"
    df_sec_cerca =pd.read_csv(url_ddist, encoding="utf-8",index_col=0) 

    df_sec_cerca.loc[(df_sec_cerca['Distancia'] == 0), 'GRUPO_DISTANCIA_PRIM'] = '0K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 0) & (df_sec_cerca['Distancia'] <= 1000), 'GRUPO_DISTANCIA_PRIM'] = 'MENOR_1K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 1000) & (df_sec_cerca['Distancia'] <= 5000), 'GRUPO_DISTANCIA_PRIM'] = '1K_5K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 5000), 'GRUPO_DISTANCIA_PRIM'] = 'MAYOR_5K'

    df_sec_cerca.columns = [x.upper() for x in df_sec_cerca.columns]
    df_sec_cerca.rename({'DISTANCIA': 'DISTANCIA_PRIM'}, axis=1, inplace=True)

    df_sec_cerca[['COD_MOD','ANEXO']] = df_sec_cerca.CODIGOLUGAR.str.split("-",expand=True)
    df_sec_cerca['ANEXO'] = df_sec_cerca['ANEXO'].astype('uint8')

    df_sec_cerca['COD_MOD']=df_sec_cerca['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    del df_sec_cerca['SECUNDARIACERCA']
    del df_sec_cerca['CODIGOLUGAR']
    
    
    return df_sec_cerca



def get_siagie_por_anio(anio,id_grado=None,id_grado_list=None,modalidad=None,modalidad_list=None,dtypes_columns=None,
                        columns_n= ['ID_PERSONA','ID_GRADO','ID_NIVEL','COD_MOD','ANEXO'],
                        id_persona_df=None,id_nivel=None,id_nivel_list=None,macro_region=None,ser_anio_menos_1=False, desercion=False, servicios = False,
                        reduce_mem_usage=False,geo=False):  
    
    if servicios:
    
        if "COD_MOD" not in  columns_n:
            columns_n.append("COD_MOD")

        if "ANEXO" not in  columns_n:
            columns_n.append("ANEXO")

    if columns_n is not None:   
    
        columns_n_aux = []
        if 'ID_PERSONA' not in columns_n:
            columns_n_aux.append('ID_PERSONA')
            
        if 'ID_GRADO' not in columns_n:
            columns_n_aux.append('ID_GRADO')
            
        if 'ID_NIVEL' not in columns_n:
            columns_n_aux.append('ID_NIVEL')    
            
        columns_n_full = columns_n+columns_n_aux
        
    else:
        columns_n_full = None
    
    dtypes_columns_d = {'COD_MOD': str,
                  #'ANEXO':int,
                  'ID_PERSONA':int,
                  'UBIGEO_NACIMIENTO_RENIEC':str,
                  'N_DOC':str,
                  'CODIGO_ESTUDIANTE':str,
                  'NUMERO_DOCUMENTO':str,
                  'N_DOC_APOD':str,
                  'CODOOII':str,
                  'ID_GRADO':'uint32',
                  'ESTADO_MAT':str,
                  'DSC_SECCION':str,
                  'ID_SECCION':str,
                  'SITUACION_MATRICULA':str,
                  'ID_NIVEL':str,
                  'SEXO':str,
                  'ANEXO': 'uint8'
                  
                  }
    
    if dtypes_columns is None:
        dtypes_columns = dtypes_columns_d

    id_niveles_inicial_ebr = ['A1','A2','A3','A5']
    if id_nivel  is not None:
        if id_nivel=="A0":      
            print("El nivel ficticio A0  sera reemplazado por los verdaderos niveles ",id_niveles_inicial_ebr)
            
    if id_nivel_list  is not None:
        if "A0" in id_nivel_list:    
            print("El nivel ficticio A0  sera reemplazado por los verdaderos niveles ",id_niveles_inicial_ebr)
     

    path_file = get_path_BD_siagie_procesado()
    
    if modalidad is None and modalidad_list is None:
        modalidad_list = []
        modalidad_list.append("EBR")
        modalidad_list.append("EBE")
    
    if modalidad_list is None and modalidad is not None:
        modalidad_list = []
        modalidad_list.append(modalidad)   
  
 
    if(anio<2018):
        url = path_file+"\\NOMINAL_{}.csv"
        
        if len(modalidad_list)==1 and id_nivel is None and  id_nivel_list is None:        
            id_nivel_list = hco.get_niveles_grados_por_modalidad(modalidad_list[0],rt_ngm=False,rt_niveles=True)
        
        iter_pd = pd.read_csv(url.format(anio), usecols=columns_n_full,encoding="latin-1",sep="|",
                              dtype=dtypes_columns,iterator=True, chunksize=500000)
        

        df = procesar_chunk_siagie(iter_pd,id_grado,id_grado_list,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr)
    else:
        multimodal = False
        if (len(modalidad_list)>1):
            multimodal = True
            
        list_df_total = []
        if ('EBR' in modalidad_list):   
            
            list_df = []
            for nivel in ["A0","B0","F0"]:               
                
                url = path_file+"\\NOMINAL_{}_{}.csv"
                iter_pd = pd.read_csv(url.format(nivel,anio), usecols=columns_n_full,encoding="latin-1",
                                      sep="|",dtype=dtypes_columns,iterator=True, chunksize=500000)
                
                df = procesar_chunk_siagie(iter_pd,id_grado,id_grado_list,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr)
                list_df.append(df)
                
            df = pd.concat(list_df)
            
            if multimodal:    
                list_df_total.append(df)
        
        if('EBE' in modalidad_list):
                url = path_file+"\\NOMINAL_{}_{}.csv"
                df = pd.read_csv(url.format("EBE",anio), usecols=columns_n_full,encoding="latin-1",sep="|",dtype=dtypes_columns)
                
                if id_grado  is not None:
                    df = df[(df['ID_GRADO'] == id_grado)] 
                    
                if id_grado_list  is not None:
                    df = df[(df['ID_GRADO'].isin(id_grado_list))] 
                    
                if id_nivel  is not None:                
                    df = df[(df['ID_NIVEL'] == id_nivel)] 
                    
                if id_nivel_list  is not None:               
                    df = df[(df['ID_NIVEL'].isin(id_nivel_list))]
                
                if id_persona_df is not None:
                    df = pd.merge(df, id_persona_df[['ID_PERSONA']], left_on="ID_PERSONA", right_on="ID_PERSONA", how='inner')
                
                if multimodal and len(df)>0: 
                    list_df_total.append(df)
                
        if multimodal:   
            df = pd.concat(list_df_total)
            
    df = df.drop_duplicates(subset=['ID_PERSONA'], keep='last')
    
    if columns_n is not None:    
        df = df[columns_n]
    
    if (macro_region   is not None) or (servicios and macro_region is None):        
        
        if ser_anio_menos_1:
            
            anio_menos_1 = anio - 1
    
            df_serv = pd.concat([get_df_servicios(macro_region=macro_region,anio=anio,geo=geo) , 
                                      get_df_servicios(macro_region=macro_region,anio=anio_menos_1,geo=geo) ])
            df_serv.drop_duplicates(subset=['COD_MOD', 'ANEXO'], keep='first',inplace=True)
            df = pd.merge(df,df_serv, left_on=["COD_MOD","ANEXO"], right_on = ["COD_MOD","ANEXO"] ,how="inner")
            
        else:            
        
            df_serv = get_df_servicios(anio=anio,macro_region=macro_region,geo=geo)
            df = pd.merge(df,df_serv, left_on=["COD_MOD","ANEXO"], right_on = ["COD_MOD","ANEXO"] ,how="inner")
            
        if servicios:
            dic_mrg = get_macro_regiones()
            for key in dic_mrg:
                #print(key, '->', dic_mrg[key])
                df.loc[(df['D_REGION'].isin(dic_mrg[key])), 'MACRO_REGION'] = key
        
        

        
        

    if desercion:   
        df_deser = get_desertores_por_anio(anio)   
        df = pd.merge(df, df_deser,left_on="ID_PERSONA", right_on="ID_PERSONA", how='left')
        
        anios_str=str(anio)+"_"+str(anio+1)
        original_col = "DESERCION_"+anios_str
        
        df.fillna({original_col:0}, inplace=True)
        
    if reduce_mem_usage:
        return hd.reduce_mem_usage(df[columns_n])
    else:    
        return df


def procesar_chunk_siagie(iter_pd,id_grado,id_grado_list,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr):
    chunk_list = []

    for chunk in iter_pd:
        if id_grado  is not None:
            chunk = chunk[(chunk['ID_GRADO'] == id_grado)] 
            
        if id_grado_list  is not None:
            chunk = chunk[(chunk['ID_GRADO'].isin(id_grado_list))]             
            
        if id_nivel  is not None:
            if id_nivel=="A0":     
                chunk = chunk[(chunk['ID_NIVEL'].isin(id_niveles_inicial_ebr))] 
            else:                  
                chunk = chunk[(chunk['ID_NIVEL'] == id_nivel)]  
        if id_nivel_list  is not None:
            if "A0" in id_nivel_list:    
                id_nivel_list.remove( "A0")                
                id_nivel_list = id_nivel_list + id_niveles_inicial_ebr                
            chunk = chunk[(chunk['ID_NIVEL'].isin(id_nivel_list))]  
        if id_persona_df is not None:
            #print(id_persona_df.shape)
            chunk = pd.merge(chunk, id_persona_df[['ID_PERSONA']], left_on="ID_PERSONA", right_on="ID_PERSONA", how='inner')
        chunk_list.append(chunk)
    return pd.concat(chunk_list)







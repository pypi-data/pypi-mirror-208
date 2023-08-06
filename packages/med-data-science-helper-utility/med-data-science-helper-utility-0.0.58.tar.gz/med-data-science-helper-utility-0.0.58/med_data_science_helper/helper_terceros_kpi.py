# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 00:36:06 2021

@author: User
"""
import pandas as pd
import numpy as np
from functools import reduce
#import core_helper.helper_acces_db as hadb

#import core_helper.helper_acces_db as hadb
#import core_helper.helper_clean as hc
#import core_helper.helper_general as hg
#import core_helper.helper_output as ho

import med_data_science_helper.helper_acces_db as hadb
import med_data_science_helper.helper_siagie_kpi as hsk

import data_science_helper.helper_clean as hc
import data_science_helper.helper_general as hg
import data_science_helper.helper_output as ho
import data_science_helper.helper_cache as hch
from datetime import datetime
from pyxlsb import convert_date
#df_siagie = hadb.get_siagie_por_anio(2022,columns_n= ['ID_PERSONA'])
#df_siagie2 = agregar_pivot_juntos(df_siagie, anio_df=2022,anio_h=2021,t_anios=3,cache=True)





def agregar_pivot_juntos(df,anio_df=None, anio_h=None , t_anios=1,delete_juntos_t_vcc=False, cache=False):
    

    ho.print_message('agregar_pivot_juntos')
    
    filename = 'agregar_pivot_juntos'
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios])
    print(key_cache)
    if cache:
        df_pivot = hch.get_cache(filename,key_cache)
        if df_pivot is not None:
            ho.print_items(df_pivot.columns,excepto=["DNI_MO"])
            if df is None:
                return 
            else:   
                #df = pd.merge(df,df_pivot, left_on=['DNI_MO','ANEXO'],right_on=['COD_MOD','ANEXO'], how='left')  
                df = pd.merge(df,df_pivot, left_on=['ID_PERSONA'],right_on=['ID_PERSONA'], how='left') 
                #df['JUNTOS'] = np.where(df['DNI_MO'].isna(), 1, 0) 
                return df  
    
    
    
    ultimo_anio, num = hsk.gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios) 
    ultimo_anio_data = ultimo_anio + 1 
    if(ultimo_anio_data<2014):            
        msg = "ERROR: Se pretende consultar hasta el anio "+str(ultimo_anio_data)+", solo se tiene data hasta el 2016"     
        raise Exception(msg) 
        
    df_id_persona = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA',"NUMERO_DOCUMENTO"])
          

      
    list_df=[]    
    for anio in range(anio_h,ultimo_anio,-1):
  
        if(anio<=2013):
            break        
  
        col_name="JUNTOS_T"
        col_VCC_name="VCC_{}_T"       

        if(num>0):
            posfix="_MENOS_{}".format(num)
            posfix_VCC="_MENOS_{}".format(num)            
            col_name = col_name+posfix
            col_VCC_name = col_VCC_name+posfix_VCC

        df_pv , periodos  = hadb.get_pivot_juntos(anio)
        print(anio)
        print(periodos)
        df_TMP = pd.merge(df_id_persona, df_pv ,left_on="NUMERO_DOCUMENTO", right_on="DNI_MO", how='left')
        
        df_TMP.drop("DNI_MO", axis = 1,inplace=True) 
        df_TMP.drop("NUMERO_DOCUMENTO", axis = 1,inplace=True) 
        
        df_TMP.fillna({'JUNTOS':0}, inplace=True)
        df_TMP.rename(columns={'JUNTOS': col_name}, inplace=True)
        
        lt_cl_vcc_delete = []
        for p in periodos:
            cl_vcc = 'VCC_{}'.format(p) 
            if col_name == "JUNTOS_T" and delete_juntos_t_vcc:     
                lt_cl_vcc_delete.append(cl_vcc)                
            else: 
                df_TMP.rename(columns={cl_vcc: col_VCC_name.format(p)}, inplace=True)
        
        if (len(lt_cl_vcc_delete)>0):
            df_TMP.drop(columns=lt_cl_vcc_delete, inplace=True)
        
        list_df.append(df_TMP)
        num+=1

    df_final_total = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df)
   

    ho.print_items(df_final_total.columns)
    hch.save_cache(df_final_total,filename,key_cache)
    
    
    if df is None:
        return 
    else:      

        df = pd.merge(df,df_final_total, left_on=['ID_PERSONA'],right_on=['ID_PERSONA'], how='left')          
        return df


def agregar_Censo_Educativo(df,df_ce=None,anio=2019, cache=False ):    
    
    ho.print_message('agregar_Censo_Educativo')
    if df_ce is None:
        df_ce = hadb.get_Censo_Educativo(anio=anio,cache=cache) 
    
    if 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    if 'ANEXO' not in df.columns:
        msg = "ERROR: No existe la columnna ANEXO en el DF proporcionado"
        raise Exception(msg)
        
    ho.print_items(df_ce.columns,excepto=['COD_MOD',"ANEXO"])
    
    if df is None:
        return 
    else:   
        df = pd.merge(df, df_ce, left_on=['COD_MOD',"ANEXO"], right_on=['COD_MOD',"ANEXO"],  how='left')    
        return df


def agregar_kpi_nexus(df,anio_df=None,df_nexus=None,anio_h=2020, cache=False ):    
    
    filename = 'agregar_kpis_nexus'
    ho.print_message('agregar_kpis_nexus')
    key_cache = hch.get_key_cache([anio_df,anio_h])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns, excepto=["COD_MOD"])            
            if df is None:
                return df_final
            else:
                df = pd.merge(df, df_final, left_on=["COD_MOD"],  right_on=["COD_MOD"],  how='left')
            return df

    ultimo_anio, num = hsk.gestionar_errores_filtro_kpi(anio_df,anio_h,1) 
    
    ho.print_message('agregar_nexus')
    if df_nexus is None:
        df_nexus = hadb.get_nexus(anio=anio_h,cache=cache) 
        df_codmod = pd.DataFrame()
        df_codmod["MODULARIE"] = df_nexus['MODULARIE'].unique()

        df_kpi_adm, df_kpi_doc, df_kpi_aux = generar_kpi_nexus_tipo_trabajador(df_nexus)
        df_kpi_jl = generar_kpi_nexus_jornada_lab(df_nexus)
        df_kpi_ed = generar_kpi_nexus_edad(df_nexus,anio_h)
        df_kpi_ge = generar_kpi_nexus_genero(df_nexus)
        df_kpi_er = generar_kpi_nexus_escala_remun(df_nexus)
        df_kpi_pl = generar_kpi_nexus_plaza(df_nexus)

        list_group = [df_codmod,df_kpi_adm,df_kpi_doc,df_kpi_aux,df_kpi_jl,df_kpi_ed,df_kpi_ge,df_kpi_er,df_kpi_pl]

        df_nexus_kpi = reduce(lambda left,right: pd.merge(left,right,on='MODULARIE',how="left"),list_group )
        df_nexus_kpi['MODULARIE']=df_nexus_kpi['MODULARIE'].astype('str')  
        df_nexus_kpi.rename(columns={"MODULARIE": "COD_MOD"},inplace=True)

    posfix="_T"
    if num>0:
        posfix="_T_MENOS_{}".format(num)
    
    for col in df_nexus_kpi.columns:
        if (col!="COD_MOD"):
            col_posfix = col+posfix
            df_nexus_kpi.rename(columns={col: col_posfix}, inplace=True)
    
    if df is not None and 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    hch.save_cache(df_nexus_kpi,filename,key_cache)    
    ho.print_items(df_nexus_kpi.columns,excepto=["COD_MOD"])
        
    if df is None:
        return df_nexus_kpi
    else:   
        df = pd.merge(df, df_nexus_kpi, left_on=["COD_MOD"], right_on=["COD_MOD"],  how='left')    
        return df


def generar_kpi_nexus_tipo_trabajador(df_nexus=None): 

    #df_nexus.rename(columns={"MODULARIE": "codmod"},inplace=True)
 
    #df_codmod = pd.DataFrame()
    #df_codmod["COD_MOD"] = df_nexus['MODULARIE'].unique()
  
    df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["DOCENTE","AUXILIAR DE EDUCACION"])==False].copy()
    df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].isin(["Activo","Encargatura"])) | (df_nexus_["ESTPLAZA"].str.contains("Designacion"))]
    df_gp_adm = get_group_nexus_ratios_codmod(df_nexus_,"ADMINISTRATIVO")

    df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["DOCENTE"])].copy()
    estado_plaza=["Activo","Encargatura","Destaque En Plaza De Profesor"]
    df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].isin(estado_plaza))]  
    df_gp_doc = get_group_nexus_ratios_codmod(df_nexus_,"DOCENTE")

    df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["AUXILIAR DE EDUCACION"])].copy()
    df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].str.contains("Activo"))] 
    df_gp_aux = get_group_nexus_ratios_codmod(df_nexus_,"AUXILIAR_EDUCACION")
 
    return df_gp_adm, df_gp_doc, df_gp_aux

def generar_kpi_nexus_jornada_lab(df_nexus_):

    df_nexus_.loc[(df_nexus_['JORNLABORAL']>=45), 'JL_MY_45_COD_MOD'] = 1
    df_nexus_.loc[(df_nexus_['JORNLABORAL']>=40) & (df_nexus_['JORNLABORAL']<45), 'JL_40_45_COD_MOD'] = 1
    df_nexus_.loc[(df_nexus_['JORNLABORAL']>=30) & (df_nexus_['JORNLABORAL']<40), 'JL_30_40_COD_MOD'] = 1
    df_nexus_.loc[(df_nexus_['JORNLABORAL']>=20) & (df_nexus_['JORNLABORAL']<30), 'JL_20_30_COD_MOD'] = 1
    df_nexus_.loc[(df_nexus_['JORNLABORAL']<20), 'JL_MN_20_COD_MOD'] = 1

    cls_jorlab = ["JL_MY_45_COD_MOD","JL_40_45_COD_MOD","JL_30_40_COD_MOD","JL_20_30_COD_MOD",
                 "JL_MN_20_COD_MOD"]   
    
    df_nexus_[cls_jorlab] = df_nexus_[cls_jorlab].fillna(0)
    df_nexus_group = df_nexus_.groupby(['MODULARIE'])[cls_jorlab].agg("sum").reset_index()

    media_std = df_nexus_.groupby(['MODULARIE'])['JORNLABORAL'].agg(['mean', 'std'])
    media_std.rename(columns={"mean": f"JL_MEAN_COD_MOD"},inplace=True)
    media_std.rename(columns={"std": f"JL_STD_COD_MOD"},inplace=True)

    df_nexus_group_jor_lab =  pd.merge(df_nexus_group,media_std,right_on='MODULARIE',left_on="MODULARIE",how="inner")

    return df_nexus_group_jor_lab


def conversion_fecha_pyxlsb(x):
    fecha = None
    try:
        fecha = convert_date(x)
    except:
        fecha = None
    return fecha


def generar_kpi_nexus_edad(df_nexus_,anio):

    df_nexus_["FECNAC_"] = df_nexus_.FECNAC.apply(conversion_fecha_pyxlsb)
    df_nexus_['FECNAC_'] = pd.to_datetime(df_nexus_['FECNAC_'], errors='coerce')
    df_nexus_ = df_nexus_[df_nexus_["FECNAC_"].isna()==False].copy() 

    dt_ref = datetime(anio, 12, 31, 0,0)
    df_nexus_['EDAD_EN_DIAS'] = dt_ref - df_nexus_['FECNAC_']
    df_nexus_['EDAD_EN_DIAS']  = df_nexus_['EDAD_EN_DIAS'].dt.days   
    df_nexus_['EDAD_CON_DECIMALES'] = df_nexus_['EDAD_EN_DIAS']/365.25
    df_nexus_['EDAD_CON_DECIMALES'] = df_nexus_['EDAD_CON_DECIMALES'].round(2)
    df_nexus_.drop(['EDAD_EN_DIAS','FECNAC_'], axis = 1,inplace=True)  

    media_std = df_nexus_.groupby(['MODULARIE'])['EDAD_CON_DECIMALES'].agg(['mean', 'std'])
    media_std.rename(columns={"mean": f"EDAD_PERSONAL_MEAN_COD_MOD"},inplace=True)
    media_std.rename(columns={"std": f"EDAD_PERSONAL_STD_COD_MOD"},inplace=True)

    return media_std

def generar_kpi_nexus_genero(df_nexus_):

    df_nexus_.loc[(df_nexus_['GENERO']=="MASCULINO"), 'T_PERSONAL_MAS_X_CMOD'] = 1
    df_nexus_.loc[(df_nexus_['GENERO']=="FEMENINO"), 'T_PERSONAL_FEM_X_CMOD'] = 1

    cls_gen = ["T_PERSONAL_MAS_X_CMOD","T_PERSONAL_FEM_X_CMOD"]   
    
    df_nexus_[cls_gen] = df_nexus_[cls_gen].fillna(0)
    df_nexus_group = df_nexus_.groupby(['MODULARIE'])[cls_gen].agg("sum").reset_index()
    df_nexus_group['TOTAL_GENERO'] = df_nexus_group[['T_PERSONAL_MAS_X_CMOD',"T_PERSONAL_FEM_X_CMOD"]].sum(axis=1)
    df_nexus_group[f'P_PERSONAL_MAS_X_CMOD']= df_nexus_group['T_PERSONAL_MAS_X_CMOD']/df_nexus_group['TOTAL_GENERO']
    df_nexus_group.drop(columns=['TOTAL_GENERO'],inplace=True)

    return df_nexus_group


def generar_kpi_nexus_escala_remun(df_nexus_):

    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="1"), 'LEY_29944_ESCALA_1'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="2"), 'LEY_29944_ESCALA_2'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="3"), 'LEY_29944_ESCALA_3'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="4"), 'LEY_29944_ESCALA_4'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="5"), 'LEY_29944_ESCALA_5'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="6"), 'LEY_29944_ESCALA_6'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="7"), 'LEY_29944_ESCALA_7'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 29944") & (df_nexus_['ESCALA REM']=="8"), 'LEY_29944_ESCALA_8'] = 1

    cls_29944 = ["LEY_29944_ESCALA_1","LEY_29944_ESCALA_2","LEY_29944_ESCALA_3","LEY_29944_ESCALA_4",
                 "LEY_29944_ESCALA_5","LEY_29944_ESCALA_6","LEY_29944_ESCALA_7","LEY_29944_ESCALA_8"]
    df_nexus_[cls_29944] = df_nexus_[cls_29944].fillna(0)

    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="1"), 'LEY_30328_ESCALA_1'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="A"), 'LEY_30328_ESCALA_A'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="B"), 'LEY_30328_ESCALA_B'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="C"), 'LEY_30328_ESCALA_C'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="D"), 'LEY_30328_ESCALA_D'] = 1
    df_nexus_.loc[(df_nexus_['DESLEY']=="LEY 30328") & (df_nexus_['ESCALA REM']=="E"), 'LEY_30328_ESCALA_E'] = 1

    cls_30328 = ["LEY_30328_ESCALA_1","LEY_30328_ESCALA_A","LEY_30328_ESCALA_B","LEY_30328_ESCALA_C",
                 "LEY_30328_ESCALA_D","LEY_30328_ESCALA_E"]
    df_nexus_[cls_30328] = df_nexus_[cls_30328].fillna(0)

    cls_ = cls_29944 + cls_30328
    df_nexus_group = df_nexus_.groupby(['MODULARIE'])[cls_].agg("sum").reset_index()

    return df_nexus_group


def generar_kpi_nexus_plaza(df_nexus_):

    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Activo', na=False)), 'AC'] = 1
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Encargatura', na=False)), 'EN'] = 1
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Abandono', na=False)), 'AD'] = 1
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Cese', na=False)), 'CS'] = 1    
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Designacion', na=False)), 'DG'] = 1
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Destaque', na=False)), 'DT'] = 1
    df_nexus_.loc[(df_nexus_['ESTPLAZA'].str.contains('Licencia', na=False)), 'LC'] = 1

    df_nexus_group = df_nexus_.groupby(['MODULARIE'])[['AC',"EN",'AD',"CS","DG","DT","LC"]].agg("sum").reset_index()
    df_nexus_group['tot_plaz_nex'] = df_nexus_group[['AC',"EN",'AD',"CS","DG","DT","LC"]].sum(axis=1)
    
    df_nexus_group[f'P_PLZ_ACTIVO_X_CMOD']= df_nexus_group['AC']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_ENCARG_X_CMOD']= df_nexus_group['EN']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_ABANDO_X_CMOD']= df_nexus_group['AD']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_CESE_X_CMOD']= df_nexus_group['CS']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_DESIGN_X_CMOD']= df_nexus_group['DG']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_DESTAQ_X_CMOD']= df_nexus_group['DT']/df_nexus_group['tot_plaz_nex']
    df_nexus_group[f'P_PLZ_LICENCIA_X_CMOD']= df_nexus_group['LC']/df_nexus_group['tot_plaz_nex']
    
    df_nexus_group.rename(columns={"AC": f"T_PLZ_ACTIVO_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"EN": f"T_PLZ_ENCARG_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"AD": f"T_PLZ_ABANDO_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"CS": f"T_PLZ_CESE_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"DG": f"T_PLZ_DESIGN_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"DT": f"T_PLZ_DESTAQ_X_CMOD"},inplace=True)
    df_nexus_group.rename(columns={"LC": f"T_PLZ_LICENCIA_X_CMOD"},inplace=True)

    df_nexus_group.drop(columns=['tot_plaz_nex'],inplace=True)
    
    return df_nexus_group


def get_group_nexus_ratios_codmod(df_nexus_,stt):
  
    df_nexus_['sitlab'] = df_nexus_['SITUACION LAB'].astype(str).str[0]

    df_nexus_['sitlab_2']='O'
   
    df_nexus_.loc[(df_nexus_['sitlab'] == "N"), 'sitlab_2'] = 'N'
    
    df_nexus_.loc[(df_nexus_['sitlab_2'] == "N"), 'N'] = 1
    df_nexus_.loc[(df_nexus_['sitlab_2'] == "O"), 'O'] = 1

  
    df_nexus_group = df_nexus_.groupby(['MODULARIE'])[["N",'O']].agg("sum").reset_index()
    df_nexus_group['tot_doc_nex'] = df_nexus_group[["N",'O']].sum(axis=1)


    df_nexus_group[f'P_{stt}_NOMB_X_CMOD']= df_nexus_group['N']/df_nexus_group['tot_doc_nex']
    df_nexus_group[f'P_{stt}_NO_NOMB_X_CMOD']= df_nexus_group['O']/df_nexus_group['tot_doc_nex']

    df_nexus_group.drop_duplicates(subset=['MODULARIE'], keep='last',inplace=True)

    #df_nexus_group.rename(columns={"MODULARIE": "COD_MOD"},inplace=True)
    
    df_nexus_group.drop(columns=['tot_doc_nex'],inplace=True)
    
    df_nexus_group.rename(columns={"N": f"T_{stt}_NOMBRADO_NEXUS"},inplace=True)
    df_nexus_group.rename(columns={"O": f"T_{stt}_NO_NOMBRADO_NEXUS"},inplace=True)

    return df_nexus_group


def agregar_ECE(df,df_ece=None,anio=2019, cache=False ):    
    
    ho.print_message('agregar_ECE')
    if df_ece is None:
        df_ece = hadb.get_ECE(anio=anio,cache=cache) 
    
    if 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    ho.print_items(df_ece.columns,excepto=['COD_MOD',"ANEXO"])   
    
    if df is None:
        return 
    else:   
        df = pd.merge(df, df_ece, left_on=['COD_MOD',"ANEXO"], right_on=['COD_MOD',"ANEXO"],  how='left')
        return df



def agregar_sisfoh(df,df_sisfoh=None, cache=False ):    
    
    ho.print_message('agregar_sisfoh')
    if cache:
        print("la cache para agregar_sisfoh no es necesario")
    if df_sisfoh is None:
        df_sisfoh = hadb.get_sisfoh()  
    
    if 'NUMERO_DOCUMENTO_APOD' not in df.columns:
        msg = "ERROR: No existe la columnna NUMERO_DOCUMENTO_APOD en el DF proporcionado"
        raise Exception(msg)
        
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].str.replace('.0', '')
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].apply(lambda x: '{0:0>8}'.format(x))
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].str.replace('00000nan', '00000000')     
    
    ho.print_items(df_sisfoh.columns,excepto=["PERSONA_NRO_DOC"])
    
    if df is None:
        return 
    else:  
        df = pd.merge(df, df_sisfoh, left_on=["NUMERO_DOCUMENTO_APOD"], right_on=["PERSONA_NRO_DOC"],  how='left')   
        df = hc.fill_nan_with_nan_category_in_cls(df , ["SISFOH_CSE"])
        del df["PERSONA_NRO_DOC"]        
        return df

# solo disponible 2019 y 2021 (EBE,) , 2020 (A0, B0 , F0, EBE). 
def agregar_shock_economico(df,df_se=None,anio=None,modalidad="EBR", cache=False ):
    
    ho.print_message('agregar_shock_economico')

    if df_se is None:
        df_se = hadb.get_shock_economico(anio,cache=cache)
    
    #print("hola")
    ho.print_items(df_se.columns)

    if df is None:
        return 
    else:  
        
        df = pd.merge(df, df_se, left_on="ID_PERSONA", right_on="ID_PERSONA",  how='left')
        return df


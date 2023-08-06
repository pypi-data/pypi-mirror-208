# -*- coding: utf-8 -*-

import med_data_science_helper.helper_siagie_kpi as hsk
import med_data_science_helper.helper_terceros_kpi as htk
import med_data_science_helper.helper_acces_db as hadb
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce
from datetime import datetime
from pyxlsb import convert_date

df_siagie = hadb.get_siagie_por_anio(2022,columns_n= ['ID_PERSONA',"COD_MOD"])

df_siagie2.shape

df_siagie2 =  htk.agregar_kpi_nexus(df_siagie,anio_df=2022,anio_h=2021, cache=True)
df_siagie2.head()

pd.set_option('display.max_columns', None)
df_kpis_nexus.head()

df_kpis_nexus.P_PLZ_ABANDO_X_CMOD_T_MENOS_1.value_counts()

df_ju =  hadb.get_juntos(anio=2022,cache=False)
df_ju.head()

df_ju.PERIODO.value_counts()
#TIPODOC_MO    DNI_MO  ANIO  PERIODO  RESULTADO_HOGAR

df_nexus = hadb.get_nexus(anio=2022,cache=True) 


df_g_edad =  htk.generar_kpi_nexus_edad(df_nexus,2022)

df_g_edad.head()
df_nexus_temp = df_nexus.copy()
df_nexus_temp.head()

df_nexus_temp.columns




df_nexus_temp["FECNAC_"].max()

df_nexus_temp.dtypes

dt_ref = datetime(2022, 12, 31, 0,0)
df_nexus_temp['EDAD_EN_DIAS'] = dt_ref - df_nexus_temp['FECNAC_']
df_nexus_temp['EDAD_EN_DIAS']  = df_nexus_temp['EDAD_EN_DIAS'].dt.days   
df_nexus_temp['EDAD_CON_DECIMALES'] = df_nexus_temp['EDAD_EN_DIAS']/365.25
df_nexus_temp['EDAD_CON_DECIMALES'] = df_nexus_temp['EDAD_CON_DECIMALES'].round(2)
df_nexus_temp.drop(['EDAD_EN_DIAS','FECNAC_'], axis = 1,inplace=True)  

df_nexus_temp.EDAD_CON_DECIMALES.max()

convert_date(21327.0)

df_gen = htk.generar_kpi_nexus_genero(df_nexus)
df_gen.head()

df_gen.TOTAL_FEMENINO.value_counts()

df_lb = htk.generar_kpi_nexus_jornada_lab(df_nexus)
df_lb.head()

df_lb["JORNLABORAL_MAYOR_45"].value_counts()
df_lb["JORNLABORAL_40_45"].value_counts()
df_lb["JORNLABORAL_30_40"].value_counts()
df_lb["JORNLABORAL_20_30"].value_counts()
df_lb["JORNLABORAL_MENOR_20"].value_counts()


df_nexus["DESLEY"].value_counts()

df_nexus_kpi =  htk.generar_kpi_nexus(df_nexus)
df_nexus_kpi.shape
df_nexus_plaza =  htk.get_ratios_plaza_codmod(df_nexus)

df_nexus_escala_renum =  htk.generar_kpi_nexus_escala_remun(df_nexus)
df_nexus_escala_renum.head()

df_nexus.JORNLABORAL.value_counts()

df_nexus_escala_renum.shape

df_nexus.columns

df_nexus.TOTAL_ADMINISTRATIVO_NOMBRADO_NEXUS.value_counts()
df_nexus.TOTAL_ADMINISTRATIVO_NO_NOMBRADO_NEXUS.value_counts()
df_nexus.TOTAL_DOCENTE_NOMBRADO_NEXUS.value_counts()
df_nexus.TOTAL_DOCENTE_NO_NOMBRADO_NEXUS.value_counts()
df_nexus.TOTAL_AUXILIAR_EDUCACION_NOMBRADO_NEXUS.value_counts()
df_nexus.TOTAL_AUXILIAR_EDUCACION_NO_NOMBRADO_NEXUS.value_counts()

def get_group_nexus_ratios_codmod(df_nexus_,stt):
  
    df_nexus_['sitlab'] = df_nexus_['SITUACION LAB'].astype(str).str[0]

    df_nexus_['sitlab_2']='O'
   
    df_nexus_.loc[(df_nexus_['sitlab'] == "N"), 'sitlab_2'] = 'N'
    
    df_nexus_.loc[(df_nexus_['sitlab_2'] == "N"), 'N'] = 1
    df_nexus_.loc[(df_nexus_['sitlab_2'] == "O"), 'O'] = 1

  
    df_nexus_group = df_nexus_.groupby(['codmod'])[["N",'O']].agg("sum").reset_index()
    df_nexus_group['tot_doc_nex'] = df_nexus_group[["N",'O']].sum(axis=1)


    df_nexus_group[f'RATIO_{stt}_NOMB_X_CMOD']= df_nexus_group['N']/df_nexus_group['tot_doc_nex']
    df_nexus_group[f'RATIO_{stt}_NO_NOMB_X_CMOD']= df_nexus_group['O']/df_nexus_group['tot_doc_nex']

    df_nexus_group.drop_duplicates(subset=['codmod'], keep='last',inplace=True)

    df_nexus_group.rename(columns={"codmod": "COD_MOD"},inplace=True)
    
    df_nexus_group.drop(columns=['tot_doc_nex'],inplace=True)
    
    df_nexus_group.rename(columns={"N": f"TOTAL_{stt}_NOMBRADO_NEXUS"},inplace=True)
    df_nexus_group.rename(columns={"O": f"TOTAL_{stt}_NO_NOMBRADO_NEXUS"},inplace=True)

    return df_nexus_group


df_codmod = pd.DataFrame()
df_codmod["COD_MOD"] = df_nexus['codmod'].unique()
df_codmod.shape

df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["DOCENTE","AUXILIAR DE EDUCACION"])==False].copy()
df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].isin(["Activo","Encargatura"])) | (df_nexus_["ESTPLAZA"].str.contains("Designacion"))]
df_group_1 = get_group_nexus_ratios_codmod(df_nexus_,"ADMINISTRATIVO")

df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["DOCENTE"])].copy()
estado_plaza=["Activo","Encargatura","Destaque En Plaza De Profesor"]
df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].isin(estado_plaza))]  
df_group_2 = get_group_nexus_ratios_codmod(df_nexus_,"DOCENTE")

df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"].isin(["AUXILIAR DE EDUCACION"])].copy()
df_nexus_ = df_nexus_[(df_nexus_["ESTPLAZA"].str.contains("Activo"))] 
df_group_3 = get_group_nexus_ratios_codmod(df_nexus_,"AUXILIAR_EDUCACION")

df_nexus_group = reduce(lambda left,right: pd.merge(left,right,on='COD_MOD',how="left"), [df_codmod,df_group_1,df_group_2,df_group_3])
    

df_group_2.shape
df_nexus_group.head()

df_group_1.columns
df_group_3.TOTAL_DOCENTE_NOMBRADO_NEXUS.value_counts()
df_group_3.TOTAL_DOCENTE_NO_NOMBRADO_NEXUS.sum() 39100.0

39100.0 + 48025.0

df_nexus_['ESTPLAZA'].value_counts()


df_nexus_ = df_nexus[df_nexus["DESCSUBTIPOTRAB"]=="AUXILIAR DE EDUCACION"].copy()

print(df_nexus_.ESTPLAZA.value_counts())

df_nexus_[df_nexus_.ESTPLAZA=="Activo"].ESTPLAZA.value_counts()

gplazas = hadb.get_ratios_plaza_codmod(df_nexus)



ax = gplazas.TOTAL_PLZ_ACTIVO_X_CMOD.hist(bins=1000)
ax.figure.savefig('./hist.png')

gplazas.RATIO_PLZ_ACTIVO_X_CMOD.value_counts()


print(gplazas.columns)

['codmod', 'TOTAL_PLZ_ACTIVO_X_CMOD', 'TOTAL_PLZ_ENCARG_X_CMOD',
       'TOTAL_PLZ_ABANDO_X_CMOD', 'TOTAL_PLZ_CESE_X_CMOD',
       'TOTAL_PLZ_DESIGN_X_CMOD', 'TOTAL_PLZ_DESTAQ_X_CMOD',
       'TOTAL_PLZ_LICENCIA_X_CMOD', 'tot_plaz_nex', 'RATIO_PLZ_ACTIVO_X_CMOD',
       'RATIO_PLZ_ENCARG_X_CMOD', 'RATIO_PLZ_ABANDO_X_CMOD',
       'RATIO_PLZ_CESE_X_CMOD', 'RATIO_PLZ_DESIGN_X_CMOD',
       'RATIO_PLZ_DESTAQ_X_CMOD', 'RATIO_PLZ_LICENCIA_X_CMOD']




print(df_nexus["SITUACION LAB"].value_counts())

print(df_nexus["CARGO"].value_counts())

print(df_nexus["NIVEL EDUCATIVO"].value_counts())

se2018 = hadb.get_shock_economico(2018,cache=True)




df_siagie = hadb.get_siagie_por_anio(2018,id_nivel="B0",id_grado=8 , columns_n= ['ID_PERSONA'])


df_siagie_ = hsk.generar_kpis_p_deser_by_dist(df_siagie,anio_df=2018 , anio_h = 2017 ,t_anios=4  ,cache=True)





df_siagie_2 = hsk.generar_kpis_p_deser_by_codmod(df_siagie,anio_df=2020 , anio_h = 2019 ,t_anios=4  ,decimals=4,cache=True)

df_p_deser = hsk.get_p_desercion_by_distrito(anio=2019,macro_region="Peru",cache=True)


df_siagie.SITUACION_FINAL.value_counts()


df_siagie[df_siagie.DESERCION_2020_2021==1].SITUACION_FINAL.value_counts()




df_siagie.columns


df_siagie_ = hsk.generar_kpis_p_deser_by_dist(df_siagie,anio_df=2021 ,cache=True)

df_siagie_2 = hsk.generar_kpis_p_deser_by_codmod(df_siagie,anio_df=2021 ,cache=True)


df_siagie_2.P_DESERCION_COD_MOD_T_MENOS_1.value_counts()

df_p_deser = hsk.get_p_desercion_by_codmod(anio=2021,macro_region="norte",cache=False)



df_siagie3 = htk.agregar_pivot_juntos(df_siagie,anio_df=2021,anio_h=2021,t_anios=3,delete_juntos_t_vcc=True, cache=False )

print(df_siagie3.columns)


print(df_siagie3.JUNTOS_T.value_counts())
print(df_siagie3.JUNTOS_T.isna().value_counts())

print(df_siagie3.JUNTOS_T_MENOS_1.isna().value_counts())
print(df_siagie3.JUNTOS_T_MENOS_1.value_counts())

print(df_siagie3.JUNTOS_T_MENOS_2.value_counts())
print(df_siagie3.JUNTOS_T_MENOS_2.isna().value_counts())

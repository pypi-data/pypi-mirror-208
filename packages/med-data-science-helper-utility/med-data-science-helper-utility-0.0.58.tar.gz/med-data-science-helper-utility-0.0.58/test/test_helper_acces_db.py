
import pandas as pd
import numpy as np
import med_data_science_helper.helper_acces_db as hadb
import med_data_science_helper.helper_siagie_kpi as hsk
import med_data_science_helper.helper_terceros_kpi as htk
import collections as c
from functools import reduce
import data_science_helper.helper_cache as hch
import data_science_helper.helper_output as ho


DF_ = hadb.get_desertores_por_anio(2021,modalidad=None)

DF_.shape


ANIO_T = 2023
modalidad = "EBR"
df_siagie_t = hadb.get_siagie_por_anio(ANIO_T,  modalidad=modalidad,  
                                       columns_n= ['ID_PERSONA',"ID_NIVEL" , "ID_GRADO",
                                                   'COD_MOD','ANEXO'],
                                       )
#(7429746, 5)
print(df_siagie_t.shape)


ANIO_T = 2023
modalidad = "EBR"
df_siagie_t = hadb.get_siagie_por_anio(ANIO_T,  modalidad=modalidad,  
                                       columns_n= ['ID_PERSONA',"ID_NIVEL" , "ID_GRADO",
                                                   'COD_MOD','ANEXO'],
                                       ser_anio_menos_1=True, servicios = True,
                                       )

df_siagie_t.MACRO_REGION.isna().value_counts()


df_siagie_t[df_siagie_t.ID_NIVEL=="A2"].ID_GRADO.value_counts()

print(df_siagie_t.shape)
df_reg =  htk.agregar_shock_economico(df_siagie_t,anio=2023,cache=False)
print(df_reg.shape)

cls_json = {}
cls_json['SITUACION_FINAL']=["APROBADO","RETIRADO"] #no aplica porque todos aprueban
cls_json['SF_RECUPERACION']=["APROBADO"] #no aplica porque todos apruban
cls_json['SITUACION_MATRICULA']=["INGRESANTE","REENTRANTE"] #no hay "REPITE" y "PROMOVIDO" esta relacionado con la no desaprobacion

kpis_hist = 5 #4 para 2020 en adelante
kpis_trl = 5 #5 para 2020 en adelante


df_reg = hsk.generar_kpis_historicos(df_siagie_t.head(10000),key_df="{}_{}".format("key_grupo_grados","macro_region"),
                                        anio_df=2021,anio_h=2020,cls_json=cls_json,t_anios=kpis_hist,cache=False)    



df_reg = hsk.generar_kpis_agg_servicios(df_siagie_t.head(10000),anio_df=2021, anio_h= 2021 , t_anios=2,cache=False)  
        
print(df_reg.columns)


df_reg.RATIO_RETIRADO_SERVICIO_T_MENOS_1.value_counts()

df_reg.columns

df_siagie = hadb.get_siagie_por_anio(2019, modalidad="EBR", columns_n= None)

df_siagie.TIENE_CERTIFICADO_DISCAPACIDAD.isna().value_counts()



Index(['ID_ANIO', 'COD_MOD', 'ANEXO', 'TIPO_DOC', 'N_DOC', 'CODIGO_ESTUDIANTE',
       'NUMERO_DOCUMENTO', 'VALIDADO_RENIEC', 'ID_PERSONA', 'NOMBRES',
       'APELLIDO_PATERNO', 'APELLIDO_MATERNO', 'DSC_LENGUA',
       'EDAD_CON_DECIMALES', 'FECHA_NACIMIENTO', 'DSC_PAIS',
       'UBIGEO_NACIMIENTO_RENIEC', 'LUGAR_NACIMIENTO_RENIEC',
       'DSC_DISCAPACIDAD', 'TIENE_CERTIFICADO_DISCAPACIDAD', 'SEXO',
       'ID_NIVEL', 'ID_GRADO', 'DSC_GRADO', 'ID_SECCION', 'DSC_SECCION',
       'ESTADO_MATRICULA', 'SITUACION_MATRICULA', 'NOMBRES_APOD',
       'APELLIDO_PATERNO_APOD', 'APELLIDO_MATERNO_APOD',
       'NUMERO_DOCUMENTO_APOD', 'VALIDADO_RENIEC_APO', 'PARENTESCO',
       'SEXO_APOD', 'NIVEL_INSTRUCCION_APOD', 'LENGUA_APOD',
       'FECHA_NACIMIENTO_APOD', 'FECHA_MATRICULA', 'FECHA_REGISTRO',
       'FECHA_DEFUNCION', 'PADRE_VIVE', 'MADRE_VIVE', 'TRABAJA',
       'HORAS_SEMANALES_TRABAJO', 'COST_CUOTA_INGRESO', 'COST_MATRICULA',
       'COST_PENSION', 'COST_APAFA', 'SITUACION_FINAL', 'SF_RECUPERACION'],
      dtype='object')

df_siagie.columns

df_siagie.MACRO_REGION.value_counts()

dic_mrg = hadb.get_macro_regiones()

for key in dic_mrg:
    print(key, '->', dic_mrg[key])
    df_siagie.loc[(df_siagie['D_REGION'].isin(dic_mrg[key])), 'MACRO_REGION'] = key

df_siagie.MACRO_REGION.value_counts()

2314620+2142414+1280114+1149432+940595+261209

df_siagie.shape

df_siagie.columns



data= ""
js_mr = hg.get_base_path()+"/config/macro_region/base.txt"
with open(js_mr) as json_file:
    data = json.load(json_file) 
        

df_siagie.D_REGION.value_counts()

anio_df = 2020
anio_h = 2020
t_anios = 5 
decimals=2

hadb.generate_lat_lon_poblacion_2017()

hadb.generate_afiliacion_salud_poblacion_2017()

hadb.generate_discapacidad_poblacion_2017()

hadb.generate_otros_poblacion_2017()


df_afiliacion_ = df.head(1000)


url_ = hadb.get_path_BD()+'\\14.Hogar_Vivienda\\otros_poblacion_2017_total.csv'  
df_ot = pd.read_csv(url_,sep='|')
df_ot.columns
#df_ot.c5_p9_7.value_counts()
df_ot_ = df_ot.head(1000)

df_ot.area.value_counts()

df_ot.c5_p28.value_counts()

df_ot.c5_p28.value_counts()



df_ot.c5_p11.value_counts()

df_ot.c5_p12.value_counts()

url_ = hadb.get_path_BD()+'\\14.Hogar_Vivienda\\discapacidad_poblacion_2017_total.csv'  
df_discap = pd.read_csv(url_,sep='|')
df_discap.columns
df_discap.c5_p9_7.value_counts()
df_discap_ = df_discap.head(1000)

url_ = hadb.get_path_BD()+'\\14.Hogar_Vivienda\\afiliacion_salud_poblacion_2017.csv'  
df_afiliacion = pd.read_csv(url_,sep='|')
df_afiliacion_ = df_afiliacion.head(1000)
df_afiliacion.columns
 
df_afiliacion.c5_p8_1.value_counts()

df_afiliacion.c5_p8_2.value_counts()



hog2017 = hadb.get_lat_lon_poblacion_2017()
hog2017 = hog2017.dropna()
url_ = hadb.get_path_BD()+'\\14.Hogar_Vivienda\\lat_lon_poblacion_2017.csv'  
hog2017.to_csv(url_, sep='|', encoding='utf-8')

hog2017.long_x.isna().value_counts()

hog2017_1  = hog2017[hog2017.c5_p10=="45249468"]


df_siagie = hadb.get_siagie_por_anio(2022,macro_region="norte" , modalidad="EBR" , id_grado_list= [9] ,columns_n= ['ID_PERSONA','COD_MOD','ANEXO','N_DOC'])

df_siagie_corr = pd.merge(df_siagie,hog2017,left_on="N_DOC",right_on="c5_p10",how="left")


df_siagie_corr.long_x.isna().value_counts()



def generar_kpis_historicos_notas(df,anio_df, anio_h, t_anios, decimals, cache=False):
    
    filename = 'kpis_historicos_notas'
    ho.print_message('agregar_kpis_historicos_notas')
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns, excepto=["COD_MOD","ANEXO"])            
            if df is None:
                return 
            else:
                df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='left')
            return df

    ultimo_anio =anio_h- t_anios
    #ultimo_anio_data = ultimo_anio + 1    
    num = anio_df-anio_h
    
    list_df_notas = []
    
    cls_list_M = []
    cls_list_C = []
    
    for anio in range(anio_h,ultimo_anio,-1):   
    
        print(anio)     
        
        col_name_C="NOTA_C_X_ALUMNO_T"
        col_name_M="NOTA_M_X_ALUMNO_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name_C = col_name_C+posfix    
            col_name_M = col_name_M+posfix  
    
        df_notas = hadb.get_df_notas(anio)   
        df_notas = df_notas[df_notas.DA.isin(["C","M"])].copy()
        
        df_notas_CM = hsk.get_df_por_alum(df_notas,'CM',[],['ID_PERSONA'])    
        print(" df_notas_CM: ",df_notas_CM.shape)
        df_notas_CM.rename({"NOTA_C_X_ALUMNO": col_name_C, "NOTA_M_X_ALUMNO": col_name_M}, axis=1, inplace=True)
        
        cls_list_M.append(col_name_M)
        cls_list_C.append(col_name_C)
        
        df_notas = None
        list_df_notas.append(df_notas_CM)
        df_notas_CM = None
        num+=1
        
    df_final = reduce(lambda left,right: pd.merge(left,right,on=["ID_PERSONA"],how='left'), list_df_notas)#.fillna(0)
    
    #df_final = df_final.head(10)
    
    cls_list_M_old_new = list(reversed(cls_list_M))
    cls_list_C_old_new = list(reversed(cls_list_C))
    
    df_final[["NOTA_M_X_ALUMNO_SLOPE","NOTA_M_X_ALUMNO_INTERCEPT","NOTA_M_X_ALUMNO_R2"]] = df_final[cls_list_M_old_new].apply(hsk.get_coeff, axis=1)
    df_final[["NOTA_C_X_ALUMNO_SLOPE","NOTA_C_X_ALUMNO_INTERCEPT","NOTA_C_X_ALUMNO_R2"]] = df_final[cls_list_C_old_new].apply(hsk.get_coeff, axis=1)
    
    
    for cl_M in cls_list_M_old_new:
        df_final["NA_"+cl_M] = np.where((df_final[cl_M].isna()),1,0)
        
    for cl_C in cls_list_C_old_new:
        df_final["NA_"+cl_C] = np.where((df_final[cl_C].isna()),1,0)        
    
    
    df_final['MEAN_NOTA_M_X_ALUMNO'] = df_final[cls_list_M_old_new].mean(axis=1)
    df_final['STD_NOTA_M_X_ALUMNO'] = df_final[cls_list_M_old_new].std(axis=1)
    
    df_final['MEAN_NOTA_C_X_ALUMNO'] = df_final[cls_list_C_old_new].mean(axis=1)
    df_final['STD_NOTA_C_X_ALUMNO'] = df_final[cls_list_C_old_new].std(axis=1)
    
    
    df_final = df_final.round({"NOTA_M_X_ALUMNO_SLOPE":decimals })
    df_final = df_final.round({"NOTA_C_X_ALUMNO_SLOPE":decimals })
    
    df_final['MEAN_NOTA_M_X_ALUMNO'] = df_final[cls_list_M].mean(axis=1)
    df_final['STD_NOTA_M_X_ALUMNO'] = df_final[cls_list_M].std(axis=1)
    
    df_final['MEAN_NOTA_C_X_ALUMNO'] = df_final[cls_list_C].mean(axis=1)
    df_final['STD_NOTA_C_X_ALUMNO'] = df_final[cls_list_C].std(axis=1)
    
    
    df_final.drop(cls_list_M_old_new, axis=1,inplace=True)
    df_final.drop(cls_list_C_old_new, axis=1,inplace=True)
    
    
    print(" df_final: ",df_final.shape)
    
    list_df_notas = None

    hch.save_cache(df_final,filename,key_cache)
    ho.print_items(df_final.columns, excepto=["ID_PERSONA"])
    if df is None:
        return 
    else:  
        df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='left')
        return df


df_siagie = hadb.get_siagie_por_anio(2022,macro_region="norte" , modalidad="EBR" , id_grado_list= [9] ,columns_n= ['ID_PERSONA','COD_MOD','ANEXO','N_DOC'])


df_siagie_ = df_siagie.head(100)


df_siagie_notas = generar_kpis_historicos_notas(df_siagie_,anio_df=2022, anio_h=2021, t_anios=4, decimals=4, cache=False)
    

#df_ = df_final.head()





df_notas = hadb.get_df_notas(2019)
df_notas = df_notas[df_notas.DA.isin(["C","M"])].copy()
df_notas_CM_t_menos_1 = hsk.get_df_por_alum(df_notas,'CM',[])

df_notas = None


if num ==0:
    cl_pf = key+"_T"              
else:
    cl_pf = key+"_T_MENOS_{}".format(num)  




df_ = df_notas_CM_t_menos_1.head()




df_notas_ = df_notas[df_notas.DA.isin(["M"])].copy()

df_ = df_notas_CM.head()

df_notas.DA.value_counts()


df_siagie_ = hadb.get_siagie_por_anio(2018,  modalidad="EBE", columns_n= ['ID_PERSONA','ID_NIVEL'])
print(" 2018  : ",df_siagie_.ID_NIVEL.value_counts())



df_serv = hadb.get_df_servicios(anio=2020,macro_region="lima_metro_callao",full=True)
print(df_serv.columns)







anio = 2020
df_siagie = hadb.get_siagie_por_anio(anio,macro_region="lima_metro_callao" ,desercion=True,  modalidad="EBR" , id_grado_list= [6,7,8] ,columns_n= ['ID_PERSONA','COD_MOD','ANEXO'])

df_siagie_ = hadb.get_siagie_por_anio(2022, modalidad="EBE", columns_n= ['ID_PERSONA','COD_MOD','ANEXO','ID_GRADO','ID_NIVEL'])



df_siagie = hadb.get_siagie_por_anio(2022,macro_region="Peru",ser_anio_menos_1 =True,modalidad="EBE", columns_n= ['ID_PERSONA','COD_MOD','ANEXO','ID_GRADO','ID_NIVEL'])




url_out ="E:\\PROYECTOS\\med-student-dropout-prediction\\src\\_04_Modeling\\modelos\\23062022\\03.data_output\\nacional_11072022_233916.dta"
df_out= pd.read_stata(url_out)  

df_siagie_out = pd.merge(df_siagie,df_out,left_on="ID_PERSONA",right_on="ID_PERSONA",how="inner")
df_siagie_out['RISK_SCORE_ROUND'] = df_siagie_out['RISK_SCORE'].round(decimals = 2)


df_siagie_out.RISK_SCORE_ROUND.value_counts()
df_siagie_out.columns



muestra = df_siagie_out[df_siagie_out.RISK_SCORE_ROUND==0.50].copy()
muestra.ID_GRADO.value_counts()

df_siagie_out.RISK_SCORE.max()




anios_str=str(anio)+"_"+str(anio+1)
original_col = "DESERCION_"+anios_str
df_siagie_ct =  pd.crosstab(index=df_siagie['D_DIST'], columns=df_siagie[original_col], normalize='index')
df_siagie_ct.rename({1: 'P_DESERCION_D_DIST', 0: 'P_SIN_DESERCION'}, axis=1, inplace=True)
df_siagie_ct.reset_index(drop=False,inplace=True)
df_siagie_ct.drop(['P_SIN_DESERCION'], axis = 1, inplace=True)


df_siagie_2020 = hadb.get_siagie_por_anio(2020,macro_region="lima_metro_callao", modalidad="EBR" , id_grado_list= [6,7,8] ,columns_n= ['ID_PERSONA','COD_MOD','ANEXO'])
df_siagie_2020 = pd.merge(df_siagie_2020, df_siagie_ct ,left_on="D_DIST",  right_on="D_DIST", how='left')











df_serv = hadb.get_df_servicios(anio=2020,macro_region="lima_metro_callao",full=True)

df_serv.columns

macro_region = "peru"
if macro_region in ["peru","perú","total","todo","general"]:
    print(True)

print(hadb.get_path_BD())



df_servicios = pd.concat([hadb.get_df_servicios(anio=2022) , hadb.get_df_servicios(anio=2021) ])
df_servicios.drop_duplicates(subset=['COD_MOD', 'ANEXO'], keep='first',inplace=True)



df_servicios = hadb.get_df_servicios(anio=2022)  
df_servicios = hadb.get_df_servicios(anio=2021)  


df = pd.merge(df_ebe,df_servicios, left_on=["COD_MOD","ANEXO"], right_on = ["COD_MOD","ANEXO"] ,how="inner")


print(df_ebe.shape)

path_file = hadb.get_path_BD_siagie_procesado()
url_trasl = path_file+'\\Siagie_Traslados_{}.csv'.format(2018)
sep = "|"
encoding = 'latin-1'
cols_tras = ['ID_PERSONA','TIPO_TRASLADO']
df_trasl = pd.read_csv(url_trasl ,encoding=encoding,usecols=cols_tras,  sep=sep,dtype={'ID_PERSONA':int})
df_merge = pd.merge(df_ebe,df_trasl,left_on = "ID_PERSONA",right_on="ID_PERSONA",how="inner")



dataSet_t = hadb.get_desertores_por_anio(2014)


dataSet_t = hadb.get_siagie_por_anio(2020,id_grado=1,id_nivel="A1",modalidad="EBR",  columns_n= ['ID_PERSONA'])
dataSet_t_menos_1 = hadb.get_siagie_por_anio(2019,modalidad_list=["EBR","EBE"],columns_n= ['ID_PERSONA'], id_persona_df=dataSet_t)    

df = hadb.get_desertores_por_anio(2019,modalidad="EBE")

df = hadb.get_nexus(anio=2015,cache=True,subtipo_trabajador=None)

df = hadb.get_ECE_2P()
df = hadb.get_ECE_4P()
df = hadb.get_ECE_2S()
df = hadb.get_ECE()

df = hadb.get_Censo_Educativo(anio=2019)

df = hadb.get_traslados_por_anio(2019)
df = hadb.get_traslados_a_publico(2019)

df = hadb.get_df_notas(2019)




df_se = hadb.get_shock_economico(2020,cache=False)

df_siagie_ebr = hadb.get_siagie_por_anio(2020,modalidad="EBR",id_nivel="A0", columns_n= ['ID_PERSONA'])  


df_siagie_ebe_ = hadb.get_siagie_por_anio(2021,modalidad_list=["EBE"],id_nivel="E2",columns_n= ['ID_PERSONA'],id_persona_df=df_siagie_ebr)  




df_siagie_ebr_ = hadb.get_siagie_por_anio(2020,modalidad_list=["EBR"],columns_n= ['ID_PERSONA'])  

df_siagie_ebe = hadb.get_siagie_por_anio(2020,modalidad="EBE",columns_n= ['ID_PERSONA'])  
df_siagie_ebe_ = hadb.get_siagie_por_anio(2020,modalidad_list=["EBE"],columns_n= ['ID_PERSONA'])  

df_siagie_total = hadb.get_siagie_por_anio(2020,modalidad_list=["EBR","EBE"],columns_n= ['ID_PERSONA'])  



df_siagie_ebr = hadb.get_siagie_por_anio(2020,modalidad="EBR",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  




df_siagie_ebe = hadb.get_siagie_por_anio(2020,modalidad="EBE",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  

df_siagie = pd.concat([df_siagie_ebr, df_siagie_ebe])  
print(df_siagie.shape)

df_serv = hadb.get_df_servicios(anio=2020,columns=["COD_MOD","ANEXO","CODGEO"])



df_merge = pd.merge(df_siagie, df_serv, left_on=["COD_MOD","ANEXO"], right_on=["COD_MOD","ANEXO"],  how='inner') 
print(df_merge.shape)

8106218-8106187

df = hadb.get_sisfoh()

df = hadb.get_distancia_prim_sec()
df = hadb.get_distancia_ini_prim()

df = hadb.get_siagie_por_anio(2020,id_nivel="A0")

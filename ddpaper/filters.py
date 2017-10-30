from __future__ import print_function


import numpy as np
import jinja2

def setup_custom_filters(latex_jinja_env):
    def format_text_exp(value):
        return "%.2lg"%value

    def format_preliminary(value):
        return "\\textcolor{red}{"+str(value)+"}"

    def format_wrt_t0(value):
        if value>0:
            return "~+~%.2lg"%abs(value)
        return "~-~%.2lg"%abs(value)

    def format_plusminus(value,ct=2):
        if np.log10(value['mean'])>3 or np.log10(value['mean'])<-2:
            value['scale_log10']=int(np.log10(value['mean']))
            if value['scale_log10']<0:
                value['scale_log10']-=1

            for v in 'mean','stat_err','stat_err_plus','stat_err_minus':
                if v in value:
                    value[v]=value[v]/10**value['scale_log10']

        if 'stat_err' in value:
            r = ("%%.%ilg~$\pm$~%%.%ilg"%(ct,ct))%(value['mean'],value['stat_err'])
        else:
            r = ("%%.%ilg\\small$^{+%%.%ilg}_{-%%.%ilg}$\\normalsize"%(ct,ct,ct))%(value['mean'],value['stat_err_plus'],value['stat_err_minus'])

        if 'scale_log10' in value:
            r+="$ \\times 10^{%i}$"%value['scale_log10']

        return r

    def format_latex_exp(value,ineq=False,mant_precision=2):
        if value is None or str(value).strip()=="" or (isinstance(value,str) and value.strip()==""):
            return "N/A"

        try:
            print("XX",value,"XX")
        except jinja2.exceptions.UndefinedError:
            return "N/A"

        try:
            value_exp=int(np.log10(value))
            if value_exp<0:
                value_exp-=1
            value_mant=value/10**value_exp
        except:
            raise

        if value_mant==10:
            value_mant=1
            value_exp+=1

        str_exp="10$^{%.2g}$"%(value_exp)
        str_mant=("%%.%ig"%mant_precision)%(value_mant)

        print("YYY::",value_mant,str_mant)

        if str_mant=="1":
            r=str_exp
        else:
            r=(str_mant+"$\\times$"+str_exp).strip()

        #r=("%.2g$\\times$10$^{%.2g}$"%(value_mant,value_exp)).strip()
        if ineq:
            r=r.replace("$","")

        print(r)

        return r

    def format_erange(value):
        if value['emax']<10000:
            return "%g~--~%g~keV"%(value['emin'],value['emax'])
        else:
            return "%g~keV~--~%g~MeV"%(value['emin'],value['emax']/1000)

    def format_utc(value):
        return value.replace("T"," ")[:19]

    latex_jinja_env.filters['wrt_t0'] = format_wrt_t0
    latex_jinja_env.filters['latex_exp'] = format_latex_exp
    latex_jinja_env.filters['text_exp'] = format_text_exp
    latex_jinja_env.filters['erange'] = format_erange
    latex_jinja_env.filters['plusminus'] = format_plusminus
    latex_jinja_env.filters['preliminary'] = format_preliminary
    latex_jinja_env.filters['format_utc'] = format_utc

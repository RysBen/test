import re
import numpy as np
import pandas as pd
import sys

# set
#pd.set_option('display.width',1000)
pd.set_option('mode.chained_assignment', None)

#***********************************splitor*****************************
patEnd_pubmedSelf = r"\[(\w?\d+;?\s?)+\]。"
pat_pubmedSelf = r"\[(\w?\d+;?\s?)+\]"
patEnd_nct = r"[（(](NCT\d+、?\s?)+[)）]。"
pat_nct = r"[（(](NCT\d+、?\s?)+[)）]"
patEnd_splitor = r"(\[(?:\w?\d+;?\s?)+\][。]|[（(](?:NCT\d+、?\s?)+[)）][。；])"   #***********************************
#***********************************************************************

def duplicate_pubmeds(x):
    no_dup = "nan"
    if not pd.isnull(x):
        no_dup = re.sub(r"(\[\w?\d+\]。)(.*)\1","。\g<2>\g<1>",x)   #****************************************** 2c: 重复出现同一pubmed
    return no_dup

#############################################################################################################
# if clinical-fda/nmpa/nccn & pubmed, then split again
#############################################################################################################
pat_fda_and_nmpa = r"(\w+)?FDA.*?NMPA.*?。"
pat_fda_or_nmpa = r"(\w+)?(FDA|NMPA).*?。"
pat_nccn = r"(\w+)?NCCN.*?。"
pat_guide = r"(" + pat_fda_and_nmpa + "|" + pat_fda_or_nmpa + "|" + pat_nccn + ")"   #******************************* 2n: FDA,NMPA,NCCN

def check_guide(e):
    check_info = "[C0]"
    if len(str(e)) < 4:
        return "[C0]"
    guides = list(set(re.findall(r"(FDA|NMPA|NCCN)", e)))
    if len(guides) > 0 :
        check_info = "[C0]clinical-" + "+".join(guides)
    return check_info

def sub_guide(e):
    c = guide_need_split(e)
    if c == "Clinical-FDA/NMPA/NCCN-No":
        e = re.sub(pat_guide, "\g<0>\n", e)
        c = "Clinical-FDA/NMPA/NCCN-2"            # 已经进一步拆分
    return e,c

def guide_need_split(e):
    check_info = ""
    if len(str(e)) < 4: return check_info
    if re.search(pat_guide, e) != None and re.search(patEnd_splitor ,e) != None:
        check_info = "Clinical-FDA/NMPA/NCCN-No"      # 需要进一步拆分
    else:
        check_info = "Clinical-FDA/NMPA/NCCN-Pass"    # 不需要进一步拆分
    return check_info

###################################################################
# status & sensitive
###################################################################
#pat_nct = r"[（(](NCT\d+、?\s?)+[)）]"   # -> pat_nct2, round3   #********************************************** nct号
pat_nct2 = r"NCT\d+"
def class_evidence(e):
    e_class = "unknown_class"
    pubmed = re.search(pat_pubmedSelf, e)
    nct = re.search(pat_nct2, e)
    if pubmed != None:
        e_class = "pubmed"
    if nct != None:
        e_class = "nct"
    if pubmed != None and nct != None:
        e_class = "pubmed_and_nct"
    return e_class

both_ntc = r"\w+.*?（NCT\d+）"
both_pubmed = r"（NCT\d+;?\s?）(.*)\[(\w?\d+;?\s?)+\]"
#
def evidence_split(evidence):
    pubmed_evidence = re.search(both_pubmed, evidence)
    nct_evidence = re.search(both_ntc, evidence)
    if pubmed_evidence != None and nct_evidence != None:
        return 'pat1', pubmed_evidence.group(0), nct_evidence.group(0)
    else:
        return 'pat2', "nan", "nan"

def status_and_sensitive(evidence_source, evidence):
    print("\n[SS]Evidence: {}".format(evidence))
    if len(str(evidence)) < 4:
        return 'nan', 'nan'
    evidence_class = class_evidence(evidence)
    if evidence_source == 'clinical':
        sensitive = 'S'
        status = clinical_status(evidence_class,evidence)
    if evidence_source == 'sensitive':
        sensitive = 'R'
        status = sensitive_status(evidence)
    return status, sensitive

def clinical_status(e_class,e):
    if e_class == 'pubmed':
        p = evidence2phase(e)
        status = 'phase-' + extract_phase(p)
    elif e_class == 'nct':
        p = evidence2phase(e)
        status = 'NCT-' + extract_phase(p)   # "NCT-?" in not allowed, need check!
    elif e_class == 'pubmed_and_nct':
        pat, pubmed_evidence, nct_evidence = evidence_split(e)   # 
        if pat == "pat1":
            p1 = evidence2phase(pubmed_evidence)
            p2 = evidence2phase(nct_evidence)
            if p1 != None:
                status = 'phase-' + extract_phase(p1)
            elif p2 != None:
                status = 'NCT-' + extract_phase(p2)
            else:
                status = 'review/phase?(02:pub_nct_both_null)'
        else:
            status = 'review/phase?(01:pubmed_nct_not_split)'
    else:
        status = 'unknown'
    return status

def sensitive_status(e):
    if re.search(r"NCCN\《", e) != None:
        status = "NCCN"
    elif re.search(r"(临床前研究|临床前[试实]验|细胞系|细胞[学]?研究|细胞对|体外[试实]验|体外细胞|功能研究|\W体外.*[实试]验\W)", e) != None:
        status = "Preclincal"
    elif re.search(r"([一1][位例名]|个案报道|临床个案|案例报道)", e) != None:
        status = "Case_report"
    else:
        status = "review/phase"
    return status
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

###################################################################
# drugs: [now]v1 ---> v2（严格匹配）
###################################################################
# v2
def extract_drugs(evidence, drug_list, drug_dict):
    drugs = [ i for i in drug_list if re.search(i, evidence, re.I) != None]
    drugs = list(set(drugs))
    #drugs_cn = [ drug_dict[i] if i in drug_dict else i for i in drugs]   #翻译
    combine_str = extract_drugs_combine(evidence, drugs)
    #drugs_cn.append(combine_str)   #去除联合用药中的药物名
    drugs_cn = merge_drugs(drugs, combine_str, drug_dict)
    return ','.join(drugs_cn)

def extract_drugs_combine(evidence, drugs):
    dd0 = "(" + '|'.join(drugs) + ")"
    dd1 = dd0 + "(?:[\(（][a-zA-Z]+?[\)）])?"
    pat1 = dd1 + "(?:联合|和|\+)" + dd1 + "(?:联合|和|\+)?" + dd0 + "?"
    combine_g = re.findall(pat1, evidence)
    if len(combine_g) == 1:
        combine_info = "+".join(combine_g[0]).strip('+')
    elif len(combine_g) > 1:
        r = []
        for i in combine_g:
            r.append("+".join(i).strip('+'))
        combine_info = ",".join(r)
    else:
        combine_info = ""
    return combine_info

def merge_drugs(drugs, combine_str, drug_dict):
    combine_ll = list(set(re.split("[+,]", combine_str)))
    combine_ll = [ drug_dict[i] if i in drug_dict else i for i in combine_ll ] # en2cn
    drugs = [ drug_dict[i] if i in drug_dict else i for i in drugs ]           # en2cn
    combine_l = re.split(",", combine_str)
    drugs2 = list(set(drugs)-set(combine_ll))                                  # difference
    drugs2 += combine_l
    return drugs2
#------------------------------------------------------------------------------------------------------------------------------------

###################################################################
# phase: [depre]v1 --> [now0315]v2（提取时期；转换字典）
###################################################################
#*******phase*******
roman = "ⅠⅡⅢⅣ"
phase1 = "I一二三四1-4" + roman

#pat_phase = r"([" + phase1 + "]+[ab]?\s?)期"
phase1 = "[一二三四1-4" + roman + "]"
#pat_phase = r"(I{1,4}|" + phase1 + ")?[ab]?/?(I{1,3}|" + phase1 +")[ab]?期"

behind_pat_phase = r"((?:I{1,4}|" + phase1 + ")[ab]?)期"
before_pat_phase = r"((?:I{1,4}|" + phase1 + ")[ab]?/(?:I{1,4}|" + phase1 + ")[ab]?)期"

######### v2
def evidence2phase(e):
    p = re.findall(behind_pat_phase, e)   # 匹配'期'字之前的时期
    if len(p) > 0:
        tmp = re.findall(before_pat_phase, e)   # 匹配'/'格式的时期（当既有'/'格式，又有正常格式时，以前者为准）
        if len(tmp) > 0:
            p = tmp
    return p   #e.g, ['1','2'],['1/2','3/4']

pat_phase_com = r"(.*)/(.*)"
def extract_phase(phases):
    result = []
    for p in phases:
        if re.match(pat_phase_com, p) != None:
            f = re.match(pat_phase_com, p).group(1)
            s = re.match(pat_phase_com, p).group(2)
            r = translate_str(f) + "/" + translate_str(s)
            result.append(r)
        else:
            result.append(translate_str(p))
    result = list(set(result))
    return ",".join(result)   # [待确认]全部保留或添加过滤条件

pat_phase_ab = r"(.*)([ab])"
def translate_str(str):
    # 时期对照字典
    phase_d = {"一": "Ⅰ", 
               "1": "Ⅰ",
               "I": "Ⅰ",
               "二": "Ⅱ",
               "2": "Ⅱ",
               "II": "Ⅱ",
               "三": "Ⅲ",
			   "3": "Ⅲ",
			   "III": "Ⅲ",
			   "4": "Ⅳ",
			   "IV": "Ⅳ",
			   "四": "Ⅳ"
              }
    if re.match(pat_phase_ab, str) != None:
        dig = re.match(pat_phase_ab, str).group(1)
        ab = re.match(pat_phase_ab, str).group(2)
    else:
        dig = str
        ab = ''
    try:
        romanDig = phase_d[dig]
    except:
        romanDig = "check_phase"
    return romanDig+ab
#---------------------------------------------------------------------------------------------------------------------------------#

###################################################################
# check
###################################################################
def check_evidence(e, drug, check):
    check_info = check.split(";")
    # 1) 疑似药物
    check1 = "[C1]"
    if len(drug) == 0:
        check1 = check_drugs_possible(e)
    check_info.append(check1)
    # 2) 抑制剂
    check2 = check_inhibitor(e)
    check_info.append(check2)
    # 3) 文献数
    check3 = check_num_evi(e)
    check_info.append(check3)
    #
    return "; ".join(check_info)

# 1) 疑似药物 [C1]
def check_drugs_possible(e):
    check = "[C1]"
    check_l = []
    possible_all = re.findall(r".{2}[a-zA-Z]+[\d]+?.{4}", e)
    if len(possible_all) > 0:
        for i in possible_all:
            pub = re.match(pat_pubmedSelf, i)      # 去除pubmed号
            nct = re.match(pat_nct2, i)             #     nct号
            shiyan = re.match(r"临床[试实]验", i)  #     临床试验
            zu = re.match(r"亚?组", i)             #     亚组
            weidian = re.match(r"位点", i)         #     位点
            jiyin = re.match(r"<i>", i)            #     基因
            if any([pub, nct, shiyan, zu, weidian, jiyin]):
                pass
            else:
                check_l += re.findall(r"[a-zA-Z]+(?:\d+)?",i)
    if len(check_l) > 0:
	    check = "[C1]疑似药物({})：{}".format(len(possible_all), ",".join(check_l))
    else:
        check = "[C1]未检测到疑似药物({})".format(len(possible_all))
    return check

# 2) 抑制剂 [C2]
inhibitor_pat = r"[a-zA-Z\d]+抑制剂"   # 1) eng/dig抑制剂; 2)[doing]中文分词？
def check_inhibitor(e):
    check = "[C2]"
    inhibitor_total = re.findall(r"抑制剂", e)
    c = len(inhibitor_total)
    if c > 0 :
        inhibitor_eng = re.findall(inhibitor_pat, e)
        inhibitor_eng = list(set(inhibitor_eng))
        if len(inhibitor_eng) > 0:
            check = "[C2]可识别抑制剂({})：{}".format(c, ",".join(inhibitor_eng))
        else:
            check = "[C2]未检测到抑制剂({})".format(c)
    return check

# 3) 文献数 [C3] -> 证据数+文献数 [C3]
pat_guide = r"(FDA|NMPA|NCCN)"
def check_num_evi(e):
    check = "[C3]"
    pubmed_num = len(re.findall(pat_pubmedSelf, e))   # how many pubmed
    nct_num = len(re.findall(pat_nct2, e))             # how many nct
    guide_num = len(re.findall(pat_guide, e))         # how many (possible) guide
    if pubmed_num >1 or nct_num >1:
        check = "[C3]两个pubmed/NCT号"
    elif pubmed_num == 0 and nct_num == 0 and guide_num == 0:
        check = "[C3]no-evidence"
    else:
        pass
    return check
#---------------------------------------------------------------------------------------------------------------------------------#


def main():
    #old_df = pd.read_excel(sys.argv[1], sheet_name='hotspot')
    old_df = pd.read_excel(sys.argv[1])
    cn2en = {'FDA/NMPA批准适应症': 'FDA/NMPA', 
             'NCCN指南推荐': 'NCCN', 
             '临床试验/回顾性分析': 'clinical', 
             '个案报道': 'case_report', 
             '临床前期证据': 'preclinical', 
             '潜在耐药药物解析': 'sensitive'}

    ###################################################
	# 1. Split Evidences, Assign Status, Assign Sensitive
    ###################################################
    final_df = pd.DataFrame()
    for k,v in cn2en.items():
        remain_cols = ['Gene', 'Tissue', 'Tissue (中文)', '核苷酸变化', 'AA(abb)', 'AA', '位点解析（中文）', k]
        new_df = old_df[remain_cols]
        ########################
        # part1: NotSplit--v--"S"
        ########################
        new_df['check'] = "[C0]" ########################################################################################## Round2
        if v in ['FDA/NMPA', 'NCCN']:
            new_df.rename(columns={k:'Evidence'}, inplace = True)
            new_df['Status'] = v
            new_df['S(sensitive)/R(resistant)'] = 'S'
        else:
            ########################
            # part2: Split--xx--xx
            ########################
            new_df[k] = new_df[k].apply(lambda x: duplicate_pubmeds(x))   #duplicate pubmeds
            new_df[k].replace(to_replace=patEnd_splitor, value="\g<0>\n", regex=True, inplace=True)
            new_df = new_df.drop(k, axis=1).join(new_df[k].str.split('\n', expand=True).stack().reset_index(level=1, drop=True).rename('Evidence'))
            ########################
            # part2-1: xx--v--"S" 
            ########################
            if v in ['case_report', 'preclinical']:
                new_df['Status'] = v
                new_df['S(sensitive)/R(resistant)'] = 'S' 
            ########################
            # part2-2: xx--f()--f()
            ########################
            else:   # v in ['clinical', 'sensitive']
                new_df['Status'], new_df['S(sensitive)/R(resistant)'] = zip(*new_df['Evidence'].apply(lambda x: status_and_sensitive(v, x)))
                if v == 'clinical':
                    new_df['check'] = new_df['Evidence'].apply(lambda x: check_guide(x))
        if final_df.empty:
            final_df = new_df
        else:
            final_df = final_df.append(new_df)
    final_df = final_df[final_df['Evidence'].map(lambda x: len(str(x))) > 3] #"", "无/略", "NaN"

    ###################################################
    # 1a. Split (Clinical-FDA/NMPA/NCCN) Evidences, Assign Status, Assign Sensitive
    ###################################################
    '''
    final_df1 = final_df[final_df['check'].str.contains('clinical')]
    final_df1['Evidence'], final_df1['check2'] = zip(*final_df1['Evidence'].apply(lambda x: sub_guide(x)))
    final_df1 = final_df1.drop('Evidence', axis=1).join(final_df1['Evidence'].str.split('\n', expand=True).stack().reset_index(level=1, drop=True).rename('Evidence'))
    
    final_df2 = final_df[~final_df['check'].str.contains('clinical')]
    final_df2['check2'] = ""
    final_df = final_df2.append(final_df1)
    '''
    ###################################################
    # 2. Drugs: extract drugs from drug sheet/...
    ###################################################
    drug_df = pd.read_excel('data/gene+drug汇总-V2-2021.3.2.xlsx', sheet_name=1)
    drug_df = drug_df['Drug'].str.split('（',expand=True).apply(lambda x: x.str.replace('）',''))
    ###
    drug_df2 = drug_df[drug_df[1].notnull()]
    drug_dict = dict(zip(drug_df2[1],drug_df2[0]))
    ###
    drug_l = pd.concat([drug_df[0],drug_df[1]]).to_list()
    drug_l = [ i for i in drug_l if i != None ]
    drug_l.append('TKI')
    ###
    final_df['Drug'] = final_df['Evidence'].apply(lambda x: extract_drugs(x,drug_l,drug_dict))
    
    ###################################################
    # for ouput
    ###################################################
    # sort by keys
    final_df = final_df.sort_values(by=['Gene','Tissue','AA'])
    # change orders of columns
    #final_df = final_df[['Gene','Tissue','Tissue (中文)', '核苷酸变化', 'AA(abb)', 'AA', 'Drug', 'Status', 'S(sensitive)/R(resistant)', 'Evidence', 'check', 'check2']]
    final_df = final_df[['Gene','Tissue','Tissue (中文)', '核苷酸变化', 'AA(abb)', 'AA', 'Drug', 'Status', 'S(sensitive)/R(resistant)', 'Evidence', 'check']]

    # check: c0,c1,c2,c3
    final_df['check'] = final_df.apply(lambda x: check_evidence(x.Evidence, x.Drug, x.check), axis=1)

    # write for debugs
    final_df.to_csv(sys.argv[2], header=True, index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    main()

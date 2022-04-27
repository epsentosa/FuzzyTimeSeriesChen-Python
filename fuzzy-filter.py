import pandas as pd
from math import log
from time import sleep

def extract_raw_data(dataframe):
    # this function should only take dataframe from pandas
    dataset = [['Years'],['\tMonth'],['Data']]
    for idx,row in dataframe.iteritems():
        data = [val for val in row[:-5]]
        if type(data[0]) is str:
            data = [i[i.find('/')+1:].replace(' ','') for i in data]
            for i in range(len(dataframe.columns)-1):
                dataset[1] += data
        elif type(data[0]) is float:
            dataset[2] += data

        if type(idx) is int:
            year = 1
            while year <= 12:
                dataset[0].append(idx)
                year += 1
    return dataset

def universe_sets(dataset_value,d1,d2):
    d_min = min(dataset_value)
    d_max = max(dataset_value)
    u_min,u_max = d_min-d1,d_max+d2
    universe_sets_val = f"[{u_min} : {u_max}]"
    return [u_min,u_max,universe_sets_val]

def extract_interval(dataset_value,u_max,u_min):
    sturges= round( 1 + 3.322 * log(len(dataset_value),10))
    class_i = round((u_max-u_min)/sturges)
    return [sturges,class_i]

def fuzzy_sets(sturges_interval,interval_u):
    fuzzy_set = {} 
    fuzzy_interval = [0.5,1,0.5] + ([0]*(sturges_interval-2))
    for i in range(1,sturges_interval+1):
        fuzz = f"A{i}"
        val = 0
        n = 1 
        for num in interval_u:
            res = fuzzy_interval[n] / num
            val += res
            n += 1
        fuzzy_set[fuzz] = val 
        fuzzy_interval.insert(0,0)
        fuzzy_interval.pop()
    return fuzzy_set

def interval_universe(sturges_interval,u_min,class_interval):
    interval_u = {}
    for i in range(1,sturges_interval+1):
        interval_u[i] = [u_min]
        u_i = u_min + class_interval
        mid = round((u_min+u_i)/2)
        interval_u[i].append(mid)
        number = str(i) + ' ' if len(str(i)) < 2 else str(i)
        print(f"{number}   u{i}=[{u_min} : {u_i}]{chr(9)} {mid}")
        u_min = u_i
    return interval_u

def fuzzification(dataset,interval_u,sturges_interval):
    dataset.append(['Fuzz..n'])
    for i in range(1, len(dataset[2])):
        data = dataset[2][i]
        n = 1
        for j in range(2,len(interval_u)+2):
            fuzz = f'A{n}'
            if n == sturges_interval:
                dataset[3].append(fuzz)
                break

            if data < interval_u[j][0]:
                dataset[3].append(fuzz)
                break
            n += 1

def set_flr_and_flrg(dataset):
    dataset.append(['FLR'])
    dataset[4].append('      ')
    flrg = {}
    for i in range(2,len(dataset[3])):
        fuzz_t = dataset[3][i-1]
        fuzz = dataset[3][i]
        flr = f'{fuzz_t}->{fuzz}'
        dataset[4].append(flr)
        group = int(fuzz_t[1:])
        if flrg.get(group) is None:
            flrg[group] = fuzz 
        else:
            if fuzz not in flrg[group]:
                flrg[group] += ',' + fuzz 

    flrg = {f"G{k}":[','.join(sorted(v.split(',')))] for k,v in sorted(list(flrg.items()))}
    # Sorted FLRG key -ex: 'A1','A2'
    for k,v in flrg.items():
        edit = v[0]
        edited = ','.join(sorted(edit.split(','),key=lambda x:int(x[1:])))
        flrg[k][0] = edited
    
    return flrg

def flrg_value(dataset,flrg):
    dataset.append(['FLRG'])

    for i in range(1,len(dataset[3])):
        data = dataset[3][i][1]
        pred = flrg[f'G{data}'][1]
        dataset[5].append(pred)

def prediction(dataset):
    dataset.append(['Prediction'])
    dataset[6].append(' ')

    for i in range(2,len(dataset[3])):
        predicted = dataset[5][i-1]
        dataset[6].append(predicted)

def set_XtFt(dataset):
    dataset.append(['(Xt-Ft)/Xt'])
    dataset[7].append(' ')

    for i in range(2,len(dataset[3])):
        data = dataset[2][i]
        pred = dataset[6][i]
        res = abs((data-pred)/data)
        res = "%.2f" % res
        dataset[7].append(res)


"""
-----------------------------------------------------
START MAIN FUNCTION
-----------------------------------------------------
"""
if __name__ == '__main__':
    #First Read Excell FIle and sync with actual excel file, below using header=3 due to file start from row 3, and then filtering column data based on used
    df = pd.read_excel('wisata asing.xls',header=3)
    df = df[['Bulan / Month',2017,2018,2019]]
    #Extract data Excell to List in python for easy access and manipulation
    dataset = extract_raw_data(df)
    #It skipped first column due to it just a Subject of column, we only need read value
    dataset_value = dataset[2][1:]
    #d1 and d2 defined by User manually
    d1,d2 = 9,34
    #Determine Universe Minimum,Maximum and Universe Sets (Himpunan Semesta)
    u_min,u_max,universe_sets_val = universe_sets(dataset_value,d1,d2)
    print("\nU = ",universe_sets_val)
    #Determine Interval using Sturges Formula
    sturges_interval,class_interval = extract_interval(dataset_value,u_max,u_min)
    print("Sturges Interval :",sturges_interval)
    print("Class Interval :",class_interval,"\n")
    #Show interval of Universe Sets and Middle Value of each interval
    print("No   Interval\t\t\t Mid Value")
    #below function also include print, if want to not show the print, just commented the print inside function
    interval_u = interval_universe(sturges_interval,u_min,class_interval)
    #Determine Fuzzy Sets
    # interval_u.append(u_max)
    # fuzzy_set = fuzzy_sets(sturges_interval,interval_u)
    # print("Fuzzy Sets")
    # for i,val in fuzzy_set.items():
            # print(i,val)

    #Create Column of fuzzification,FLRG,Predicted Value, and value of (Xt-Ft)/Xt
    fuzzification(dataset,interval_u,sturges_interval)
    flrg = set_flr_and_flrg(dataset)
    # print FLRG and do Deffuzification
    print("\nDeffuzification")
    for k,v in flrg.items():
        key = k[1]
        m = [interval_u[int(i[1])][1] for i in flrg[k][0].split(',')]
        pred = int(sum(m)/len(m))
        flrg[k].append(pred)

    print("Group    FLRG","\t\t","       Prediction")
    for k,v in flrg.items():
        v_flrg,v_pred = v[0],v[1]
        v_flrg = str(v_flrg) + '\t\t' if len(str(v_flrg)) < 6 else str(v_flrg) + '\t' if len(str(v_flrg)) < 14 else str(v_flrg)
        print(k,"\t",v_flrg,'\t',v_pred)
    print("------------------------------------------------------------------------------------------------------------------------------------\n")

    flrg_value(dataset,flrg)
    prediction(dataset)
    set_XtFt(dataset)
    # Print All Column and Result
    year,month,data,fuzzification,flr,flrg,prediction,xtft = dataset[0][0],dataset[1][0],dataset[2][0],dataset[3][0],dataset[4][0],dataset[5][0],dataset[6][0],dataset[7][0]
    print(f"{year}{month}    {data}\t    {fuzzification}\t{flr}\t  {flrg}\t\t{prediction}  {xtft}")
    for i in range(1,len(dataset[0])):
        year,month,data = dataset[0][i],dataset[1][i],dataset[2][i]
        data = str(data) + ' ' if len(str(data)) < 8 else str(data)
        fuzz = dataset[3][i]
        fuzz = str(fuzz) + ' ' if len(str(fuzz)) < 3 else str(fuzz)
        flr = dataset[4][i]
        flr = str(flr) + '  ' if len(str(flr)) < 7 else str(flr) + ' ' if len(str(flr)) < 8 else str(flr)
        flrg_val = dataset[5][i]
        predicted_val = dataset[6][i]
        predicted_val = str(predicted_val) + ' ' if len(str(predicted_val)) < 6 else str(predicted_val)
        xrft = '  ' + str(dataset[7][i])
        print(year,month,'\t',data,'    ',fuzz,'  ',flr,'  ',flrg_val,'\t',predicted_val,'    ',xrft)
        # sleep(0.05)

    #below printed Total value of XtFt and then can be found of MAPE value
    xtft = [float(i) for i in dataset[7][2:]]
    total = sum(xtft)
    print("\t\t\tTotal\t\t\t\t\t\t    ","%.2f" % total)
    print()
    mape = (total/len(dataset[2][1:]))*100
    mape = "%.2f" % mape
    sleep(0.3)
    print("MAPE is ",mape,"%")
    
    #The Result prediction of next month is just take last index value of FLRG value
    print("Value predicted of Next Month (January 2020) is",dataset[5][-1])

def calcular_parcela_price(valor, taxa, prazo): 
    v = valor
    i = taxa
    n = prazo
    
    pmt = v * i / (1 - (1 + i) ^ (-n)) 

    return pmt



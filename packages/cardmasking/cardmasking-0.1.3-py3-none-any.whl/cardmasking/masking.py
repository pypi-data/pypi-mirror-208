
def cardmapping(card,cvv,expiryMonth,expiryYear):
    x = 0
    card_num =""
    cvv_num =""
    expiry_year = ""
    expiry_month = ""
    for i in card:
        if x >3 and x<12:
            card_num += "*"
        else:
            card_num+=i
        x+=1

    for i in cvv:
        cvv_num += "*"

    for i in expiryYear:
        expiry_year += "*"

    for i in expiryMonth:
        expiry_month += "*"

    response = {
        "card":card_num,
        "cvv":cvv_num,
        "expiryyear":expiry_year,
        "expirymonth":expiry_month
    }
        
    return response
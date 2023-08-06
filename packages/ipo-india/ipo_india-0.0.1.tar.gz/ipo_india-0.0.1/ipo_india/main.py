from ipo_india.ipo import Ipo
from ipo_india.ipo_scraper import TopShareBrokersIPO

def get_ipos(readable: bool = False,
             open_ipos: bool = False,
             retail: bool = False,
             sme: bool = False):
    try:
        if open_ipos:
            if retail:
                ipos = TopShareBrokersIPO.get_open_retail_ipos()
            elif sme:
                ipos = TopShareBrokersIPO.get_open_sme_ipos()
            else:
                ipos = TopShareBrokersIPO.get_open_ipos()
        else:
            ipos = TopShareBrokersIPO.get_ipos()
        
        if readable:
            ipos = [str(Ipo(name=ipo_name, **ipo_data)) for ipo_name, ipo_data in ipos.items()]
        else:
            ipos = [Ipo(name=ipo_name, **ipo_data) for ipo_name, ipo_data in ipos.items()]

        return ipos
    except Exception:
        raise Exception("Faield to get IPOs")

# ipos = get_ipos(readable=True, open_ipos=False)
ipos = get_ipos(open_ipos=False)

print(ipos)
print(ipos.sort(key=lambda x: x.open_date))
print(ipos.sort(key=lambda x: x.open_date, reverse=True))
print(ipos)